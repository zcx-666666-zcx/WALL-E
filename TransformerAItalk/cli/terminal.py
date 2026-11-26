"""
终端对话调试界面（CLI）
────────────────────────────────────────────────────────────────
功能：
  · 彩色终端输出，流式打字效果
  · /help        查看所有命令
  · /persona     切换 / 查看人设
  · /memory      查看 / 编辑用户记忆
  · /emotion     查看情感检测结果
  · /history     查看本轮对话历史
  · /clear       清空本轮历史
  · /new_persona 创建自定义人设
  · /train       快速触发训练任务
  · /stats       查看用户情感趋势统计
  · /debug       切换调试信息显示
  · /quit        退出

启动方式：
    python -m cli.terminal
    python -m cli.terminal --persona grandpa_li --user 老王
    python -m cli.terminal --demo    # 无 GPU 演示模式
"""

from __future__ import annotations
import sys
import os
import argparse
try:
    import readline          # Linux / Mac 上下键翻历史
except ImportError:
    try:
        import pyreadline3   # Windows 替代（pip install pyreadline3）
    except ImportError:
        pass                 # 无历史功能，不影响主流程
from datetime import datetime

# ── 颜色常量（ANSI）─────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
MAGENTA= "\033[95m"
WHITE  = "\033[97m"
BG_DARK= "\033[40m"

def c(text, *codes):
    return "".join(codes) + str(text) + RESET


# ════════════════════════════════════════════
# 终端会话
# ════════════════════════════════════════════

class TerminalSession:
    """
    终端对话会话管理器
    封装所有 CLI 交互逻辑
    """

    BANNER = f"""
{CYAN}{BOLD}
  ╔═══════════════════════════════════════╗
  ║        🌸  Elder AI  🌸               ║
  ║      适老化情感陪伴系统 v1.0           ║
  ╚═══════════════════════════════════════╝
{RESET}{DIM}  输入 /help 查看所有命令  |  /quit 退出{RESET}
"""

    HELP = f"""
{BOLD}{'─'*45}{RESET}
{CYAN}对话命令{RESET}
  /persona [id]     查看/切换人设
  /new_persona      交互式创建自定义人设
  /memory           查看当前用户记忆
  /memory set       编辑用户信息
  /emotion          查看最近一次情感检测
  /history          查看本轮对话历史
  /clear            清空本轮对话历史
  /stats            情感趋势统计

{CYAN}系统命令{RESET}
  /debug            切换调试信息显示
  /train emotion    训练情感模型（需指定数据路径）
  /train persona    训练人设适配器（需指定数据路径）
  /user [name]      切换用户
  /save             手动保存用户记忆
  /help             显示此帮助
  /quit             退出程序
{'─'*45}
"""

    def __init__(
        self,
        user_id: str = "default_user",
        persona_id: str = "grandma_chen",
        demo_mode: bool = False,
        show_debug: bool = False,
    ):
        self.user_id = user_id
        self.current_persona_id = persona_id
        self.demo_mode = demo_mode
        self.show_debug = show_debug

        self.history: list[dict] = []       # 本轮对话历史
        self._last_emotion = None

        # 延迟导入（避免启动时等待模型加载）
        self._init_components()

    def _init_components(self):
        print(c("正在初始化组件…", DIM))

        from personas.persona_manager import PersonaManager
        from memory.user_memory import UserMemory
        from core.emotion import EmotionDetector
        from core.engine import DialogueEngine
        from config.settings import MAX_HISTORY_TURNS

        self.pm = PersonaManager()
        self.memory = UserMemory(self.user_id)
        self.emotion_detector = EmotionDetector()
        self.engine = DialogueEngine()
        self.max_history = MAX_HISTORY_TURNS

        print(c("加载对话引擎…", DIM))
        self.engine.load(force_demo=self.demo_mode)

        # 切换到初始人设
        self._switch_persona(self.current_persona_id, silent=True)

    # ════════════════════════════════════════
    # 主循环
    # ════════════════════════════════════════

    def run(self):
        print(self.BANNER)
        self._print_persona_card()
        print()

        while True:
            try:
                user_input = input(c(f"\n你  ", CYAN, BOLD)).strip()
            except (EOFError, KeyboardInterrupt):
                self._quit()
                return

            if not user_input:
                continue

            if user_input.startswith("/"):
                self._handle_command(user_input)
            else:
                self._chat(user_input)

    # ════════════════════════════════════════
    # 对话处理
    # ════════════════════════════════════════

    def _chat(self, text: str):
        # 情感检测
        emotion = self.emotion_detector.detect(text)
        self._last_emotion = emotion

        if self.show_debug:
            print(c(f"  {emotion}", DIM, YELLOW))

        # 截断历史
        trimmed_history = self.history[-(self.max_history * 2):]

        # 显示 AI 名字
        persona = self.pm.get(self.current_persona_id)
        print(c(f"\n{persona.name}  ", MAGENTA, BOLD), end="", flush=True)

        # 流式输出
        full_reply = ""
        try:
            for chunk in self.engine.stream(
                persona, trimmed_history, text, self.memory, emotion
            ):
                print(chunk, end="", flush=True)
                full_reply += chunk
        except Exception as e:
            print(c(f"\n[错误] 生成失败：{e}", RED))
            return

        print()  # 换行

        # 更新历史
        self.history.append({"role": "user", "content": text})
        self.history.append({"role": "assistant", "content": full_reply})

        # 更新记忆
        self.memory.update_emotion(emotion.emotion, emotion.confidence)
        self.memory.increment_chat()

        # 情感关怀提示
        if emotion.needs_care and self.show_debug:
            print(c(f"  ⚠ 检测到需要关怀情绪：{emotion.emotion}", YELLOW, DIM))

    # ════════════════════════════════════════
    # 命令处理
    # ════════════════════════════════════════

    def _handle_command(self, cmd: str):
        parts = cmd.strip("/").split(maxsplit=1)
        name = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        dispatch = {
            "help":        lambda: print(self.HELP),
            "quit":        self._quit,
            "exit":        self._quit,
            "q":           self._quit,
            "persona":     lambda: self._cmd_persona(arg),
            "new_persona": self._cmd_new_persona,
            "memory":      lambda: self._cmd_memory(arg),
            "emotion":     self._cmd_emotion,
            "history":     self._cmd_history,
            "clear":       self._cmd_clear,
            "stats":       self._cmd_stats,
            "debug":       self._cmd_debug,
            "user":        lambda: self._cmd_user(arg),
            "save":        lambda: (self.memory.save(), print(c("记忆已保存 ✓", GREEN))),
            "train":       lambda: self._cmd_train(arg),
        }

        handler = dispatch.get(name)
        if handler:
            handler()
        else:
            print(c(f"未知命令 /{name}，输入 /help 查看所有命令", YELLOW))

    # ── /persona ────────────────────────────
    def _cmd_persona(self, arg: str):
        if not arg:
            # 列出所有人设
            print(c(f"\n{'─'*40}", DIM))
            print(c(" 可用人设", BOLD))
            print(c(f"{'─'*40}", DIM))
            for p in self.pm.list_all():
                active = " ← 当前" if p["id"] == self.current_persona_id else ""
                tag = c(f"[{p['type']}]", CYAN if p["type"] == "内置" else YELLOW)
                print(f"  {tag} {c(p['id'], BOLD)}  {p['name']}({p['age']}岁)"
                      f"  {c(p['personality'], DIM)}{c(active, GREEN)}")
            print()
            print(c("  切换：/persona <id>", DIM))
        else:
            self._switch_persona(arg)

    def _switch_persona(self, persona_id: str, silent: bool = False):
        try:
            _ = self.pm.get(persona_id)
            self.current_persona_id = persona_id
            # 尝试加载 LoRA 适配器
            has_adapter = self.engine.load_adapter(persona_id)
            if not silent:
                self._print_persona_card()
                if has_adapter:
                    print(c("  已加载专属 LoRA 人设适配器 ✓", GREEN, DIM))
        except ValueError as e:
            print(c(f"错误：{e}", RED))

    def _print_persona_card(self):
        p = self.pm.get(self.current_persona_id)
        print(c(f"\n{'─'*40}", DIM))
        print(f"  {c('当前人设', BOLD)}  {c(p.name, CYAN, BOLD)} · {p.age}岁")
        print(f"  {c('性格', DIM)}  {p.personality[:40]}")
        print(f"  {c('风格', DIM)}  {p.speaking_style[:40]}")
        print(c(f"{'─'*40}", DIM))

    # ── /new_persona ─────────────────────────
    def _cmd_new_persona(self):
        print(c("\n创建自定义人设（输入空白跳过可选项）", CYAN, BOLD))
        print(c("─"*40, DIM))

        def ask(prompt, required=True):
            while True:
                val = input(c(f"  {prompt}：", YELLOW)).strip()
                if val or not required:
                    return val
                print(c("  此项必填", RED))

        persona_id   = ask("人设ID（英文，如 my_grandma）")
        name         = ask("名字")
        age          = int(ask("年龄") or "65")
        background   = ask("背景故事")
        personality  = ask("性格描述")
        speaking_style = ask("说话风格")
        catchphrases = [x.strip() for x in ask("口头禅（逗号分隔，可空）", False).split("，") if x.strip()]
        topics       = [x.strip() for x in ask("感兴趣话题（逗号分隔，可空）", False).split("，") if x.strip()]

        try:
            p = self.pm.create(
                persona_id=persona_id, name=name, age=age,
                background=background, personality=personality,
                speaking_style=speaking_style,
                catchphrases=catchphrases, topics_of_interest=topics,
            )
            print(c(f"\n人设 {name} 创建成功！", GREEN))
            print(c("  切换到新人设：/persona " + persona_id, DIM))
            print(c("\n生成的 System Prompt 预览：", DIM))
            print(c("─"*40, DIM))
            print(p.system_prompt[:400] + ("…" if len(p.system_prompt) > 400 else ""))
        except Exception as e:
            print(c(f"创建失败：{e}", RED))

    # ── /memory ──────────────────────────────
    def _cmd_memory(self, arg: str):
        if arg == "set":
            print(c("\n编辑用户信息（回车跳过）", CYAN))
            name = input(c(f"  姓名 [{self.memory.data.get('name','')}]：", YELLOW)).strip()
            age  = input(c(f"  年龄 [{self.memory.data.get('age','')}]：", YELLOW)).strip()
            loc  = input(c(f"  所在地 [{self.memory.data.get('location','')}]：", YELLOW)).strip()
            upd = {}
            if name: upd["name"] = name
            if age:  upd["age"] = int(age)
            if loc:  upd["location"] = loc
            if upd:
                self.memory.update_profile(**upd)
                print(c("用户信息已更新 ✓", GREEN))
        else:
            d = self.memory.data
            print(c(f"\n{'─'*40}", DIM))
            print(c(" 用户记忆", BOLD))
            print(c(f"{'─'*40}", DIM))
            print(f"  ID          {d['user_id']}")
            print(f"  姓名        {d['name'] or c('未设置', DIM)}")
            print(f"  年龄        {d['age'] or c('未设置', DIM)}")
            print(f"  地区        {d['location'] or c('未设置', DIM)}")
            print(f"  对话次数    {d['chat_count']}")
            print(f"  兴趣爱好    {', '.join(d['interests']) or c('无', DIM)}")
            print(f"  健康备注    {'; '.join(d['health_notes'][-3:]) or c('无', DIM)}")
            recent = [e['emotion'] for e in d['emotion_log'][-5:]]
            print(f"  近期情绪    {' → '.join(recent) if recent else c('暂无', DIM)}")
            ctx = self.memory.context_summary()
            if ctx:
                print(f"\n  {c('记忆摘要（注入Prompt）', DIM)}")
                print(f"  {c(ctx, DIM)}")
            print()

    # ── /emotion ─────────────────────────────
    def _cmd_emotion(self):
        if self._last_emotion is None:
            print(c("尚未进行情感检测，请先发送一条消息", YELLOW))
            return
        e = self._last_emotion
        print(c(f"\n{'─'*40}", DIM))
        print(c(" 情感检测结果", BOLD))
        print(c(f"{'─'*40}", DIM))
        print(f"  主情感   {c(e.emotion, CYAN, BOLD)}  {c(f'{e.confidence:.0%}', GREEN)}")
        print(f"  需关怀   {'是 ⚠' if e.needs_care else '否'}")
        print(f"\n  全类别分布：")
        for emotion, score in sorted(e.all_scores.items(), key=lambda x: -x[1]):
            bar_len = int(score * 20)
            bar = c("█" * bar_len, CYAN) + c("░" * (20 - bar_len), DIM)
            print(f"    {emotion:4s} {bar} {score:.1%}")
        print()

    # ── /history ─────────────────────────────
    def _cmd_history(self):
        if not self.history:
            print(c("本轮暂无对话历史", YELLOW))
            return
        print(c(f"\n{'─'*40}", DIM))
        print(c(f" 对话历史（{len(self.history)//2} 轮）", BOLD))
        print(c(f"{'─'*40}", DIM))
        for i, msg in enumerate(self.history):
            role = c("你", CYAN) if msg["role"] == "user" else c("AI", MAGENTA)
            text = msg["content"]
            if len(text) > 60:
                text = text[:60] + "…"
            print(f"  {role}  {text}")
        print()

    # ── /clear ───────────────────────────────
    def _cmd_clear(self):
        self.history.clear()
        print(c("对话历史已清空 ✓", GREEN))

    # ── /stats ───────────────────────────────
    def _cmd_stats(self):
        trend = self.memory.emotion_trend(last_n=20)
        if not trend:
            print(c("情感数据不足，请多聊一会儿", YELLOW))
            return
        print(c(f"\n{'─'*40}", DIM))
        print(c(f" 情感趋势（最近20条）", BOLD))
        print(c(f"{'─'*40}", DIM))
        for emotion, ratio in trend.items():
            bar_len = int(ratio * 25)
            bar = c("█" * bar_len, CYAN) + c("░" * (25 - bar_len), DIM)
            print(f"  {emotion:4s} {bar} {ratio:.0%}")
        print()

    # ── /debug ───────────────────────────────
    def _cmd_debug(self):
        self.show_debug = not self.show_debug
        status = c("开启", GREEN) if self.show_debug else c("关闭", YELLOW)
        print(c(f"调试信息已{status}", DIM))

    # ── /user ────────────────────────────────
    def _cmd_user(self, arg: str):
        if not arg:
            print(c(f"当前用户 ID：{self.user_id}", CYAN))
            return
        from memory.user_memory import UserMemory
        self.memory.save()
        self.user_id = arg
        self.memory = UserMemory(arg)
        self.history.clear()
        print(c(f"已切换到用户 {arg}，对话历史已清空", GREEN))

    # ── /train ───────────────────────────────
    def _cmd_train(self, arg: str):
        parts = arg.split()
        if not parts:
            print(c("用法：/train emotion --data <路径>  |  /train persona --persona <id> --data <路径>", YELLOW))
            return
        task = parts[0]
        if task == "emotion":
            data = self._find_flag(parts, "--data")
            if not data:
                data = input(c("  情感训练数据路径：", YELLOW)).strip()
            print(c(f"启动情感分类训练…", CYAN))
            from training.trainer import EmotionTrainer
            EmotionTrainer(data).train()
        elif task == "persona":
            pid  = self._find_flag(parts, "--persona") or self.current_persona_id
            data = self._find_flag(parts, "--data")
            if not data:
                data = input(c("  人设训练数据路径：", YELLOW)).strip()
            print(c(f"启动 {pid} 人设微调训练…", CYAN))
            from training.trainer import PersonaTrainer, PersonaTrainConfig
            PersonaTrainer(PersonaTrainConfig(persona_id=pid, data_path=data)).train()
        else:
            print(c(f"未知训练任务：{task}", RED))

    @staticmethod
    def _find_flag(parts: list, flag: str) -> str | None:
        try:
            idx = parts.index(flag)
            return parts[idx + 1]
        except (ValueError, IndexError):
            return None

    # ── /quit ────────────────────────────────
    def _quit(self):
        self.memory.save()
        print(c("\n记忆已保存，再见！👋\n", CYAN))
        sys.exit(0)


# ════════════════════════════════════════════
# 程序入口
# ════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Elder AI 终端调试界面")
    parser.add_argument("--user",    default="default_user", help="用户 ID")
    parser.add_argument("--persona", default="grandma_chen", help="初始人设 ID")
    parser.add_argument("--demo",    action="store_true",    help="演示模式（无需 GPU）")
    parser.add_argument("--debug",   action="store_true",    help="显示调试信息")
    args = parser.parse_args()

    session = TerminalSession(
        user_id=args.user,
        persona_id=args.persona,
        demo_mode=args.demo,
        show_debug=args.debug,
    )
    session.run()


if __name__ == "__main__":
    main()
