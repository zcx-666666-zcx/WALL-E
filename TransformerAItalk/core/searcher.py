"""
联网搜索模块
触发条件：用户消息包含时效性关键词
搜索结果注入 Prompt，让瓦利基于真实信息回答
"""
from __future__ import annotations
from config.settings import TAVILY_API_KEY, SEARCH_ENABLED, SEARCH_TRIGGER_KEYWORDS


def needs_search(text: str) -> bool:
    """判断用户输入是否需要联网搜索"""
    if not SEARCH_ENABLED:
        return False
    return any(kw in text for kw in SEARCH_TRIGGER_KEYWORDS)


def search(query: str, max_results: int = 3) -> str:
    """
    执行搜索，返回格式化的搜索结果文本
    失败时返回空字符串，不影响正常对话
    """
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=True,   # 让 Tavily 直接给一个摘要答案
        )

        parts = []

        # Tavily 的直接摘要
        if response.get("answer"):
            parts.append(f"搜索摘要：{response['answer']}")

        # 各条搜索结果
        for r in response.get("results", []):
            parts.append(
                f"来源：{r.get('title', '')}\n"
                f"内容：{r.get('content', '')[:200]}"  # 只取前200字
            )

        return "\n\n".join(parts) if parts else ""

    except Exception as e:
        print(f"[搜索] 失败：{e}")
        return ""