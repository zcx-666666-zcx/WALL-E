package com.example.demo.controller;

import com.example.demo.common.Result;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StreamUtils;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/news")
@CrossOrigin(origins = "*")
public class NewsController {

    // 定义上传目录
    private static final String UPLOAD_DIR = "uploads/news_index/";

    /**
     * 获取新闻详情
     *
     * @param id 新闻ID
     * @return 新闻详情
     */
    @GetMapping("/{id}")
    public ResponseEntity<Result<Map<String, Object>>> getNewsDetail(@PathVariable Long id) {
        Map<String, Object> newsDetail = new HashMap<>();

        try {
            // 图片路径
            String imagePath = "/uploads/news_index/news_" + id + ".jpg";

            // 尝试读取文本内容
            String textContent = readTextContent(id);

            // 构建返回数据
            newsDetail.put("id", id);
            newsDetail.put("title", "新闻标题 " + id);
            newsDetail.put("image", imagePath);
            newsDetail.put("description", textContent);
            newsDetail.put("publishTime", "2024-06-01 12:00:00");
            newsDetail.put("author", "非遗文化编辑部");

            return ResponseEntity.ok(Result.success(newsDetail));
        } catch (Exception e) {
            // 出错时使用默认内容
            newsDetail.put("id", id);
            newsDetail.put("title", "新闻标题 " + id);
            newsDetail.put("image", "/uploads/news_index/news_" + id + ".jpg");
            newsDetail.put("description", "这是新闻ID为 " + id + " 的详细内容。在这里可以展示非遗项目的详细介绍、历史渊源、传承现状等等。非遗文化是中华民族的瑰宝，值得我们去传承和发扬光大。");
            newsDetail.put("publishTime", "2024-06-01 12:00:00");
            newsDetail.put("author", "非遗文化编辑部");

            return ResponseEntity.ok(Result.success(newsDetail));
        }
    }

    /**
     * 读取指定ID的文本内容
     *
     * @param id 新闻ID
     * @return 文本内容
     * @throws IOException 读取文件异常
     */
    private String readTextContent(Long id) throws IOException {
        // 尝试多种文本文件格式
        String[] extensions = {".txt", ".md"};
        for (String ext : extensions) {
            Path textPath = Paths.get(UPLOAD_DIR + "news_" + id + ext);
            if (Files.exists(textPath)) {
                return Files.readString(textPath, StandardCharsets.UTF_8);
            }
        }
        // 如果没找到文本文件，返回默认内容
        return "这是新闻ID为 " + id + " 的详细内容。在这里可以展示非遗项目的详细介绍、历史渊源、传承现状等等。非遗文化是中华民族的瑰宝，值得我们去传承和发扬光大。";
    }

    /**
     * 获取最近新闻列表
     *
     * @return 最近新闻列表
     */
    @GetMapping("/recent")
    public ResponseEntity<Result<Object>> getRecentNews() {
        return ResponseEntity.ok(Result.success("success"));
    }

    // 搜索功能（简单实现）
    @GetMapping("/search")
    public ResponseEntity<Result<Object>> searchNews(@RequestParam String keyword) {
        return ResponseEntity.ok(Result.success("success"));
    }
}