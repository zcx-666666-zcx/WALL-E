package com.example.demo.controller;

import com.example.demo.common.Result;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/files")
@CrossOrigin(origins = "*")
public class FileUploadController {

    // 定义文件上传目录
    private static final String UPLOAD_DIR = "uploads/";

    /**
     * 上传图片文件
     * @param file 上传的文件
     * @return 上传结果和文件访问URL
     */
    @PostMapping("/upload-image")
    public ResponseEntity<Result<Map<String, String>>> uploadImage(@RequestParam("file") MultipartFile file) {
        // 检查文件是否为空
        if (file.isEmpty()) {
            return ResponseEntity.ok(Result.error("上传文件不能为空"));
        }

        try {
            // 检查上传目录是否存在，不存在则创建
            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // 获取原始文件名
            String originalFilename = file.getOriginalFilename();
            
            // 生成唯一文件名
            String extension = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String uniqueFilename = UUID.randomUUID().toString() + extension;
            
            // 构建文件保存路径
            Path filePath = uploadPath.resolve(uniqueFilename);
            
            // 保存文件
            Files.write(filePath, file.getBytes());
            
            // 构造文件访问URL
            String fileUrl = "/uploads/" + uniqueFilename;
            
            // 返回结果
            Map<String, String> responseData = new HashMap<>();
            responseData.put("url", fileUrl);
            responseData.put("filename", uniqueFilename);
            
            return ResponseEntity.ok(Result.success("文件上传成功", responseData));
        } catch (IOException e) {
            return ResponseEntity.ok(Result.error("文件上传失败: " + e.getMessage()));
        }
    }
}