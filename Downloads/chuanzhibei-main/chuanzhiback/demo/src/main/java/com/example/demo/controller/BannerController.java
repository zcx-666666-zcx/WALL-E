package com.example.demo.controller;

import com.example.demo.entity.Banner;
import com.example.demo.service.BannerService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/banners")
@CrossOrigin(origins = "*")
public class BannerController {

    @Autowired
    private BannerService bannerService;

    @GetMapping
    public ResponseEntity<Result<List<Banner>>> getAllBanners() {
        List<Banner> banners = bannerService.getAllBanners();
        return ResponseEntity.ok(Result.success(banners));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Result<Banner>> getBannerById(@PathVariable Long id) {
        Banner banner = bannerService.getBannerById(id);
        if (banner != null) {
            return ResponseEntity.ok(Result.success(banner));
        } else {
            return ResponseEntity.ok(Result.error("轮播图不存在"));
        }
    }

    @PostMapping
    public ResponseEntity<Result<Banner>> createBanner(@RequestBody Banner banner) {
        Banner savedBanner = bannerService.saveBanner(banner);
        return ResponseEntity.ok(Result.success("轮播图创建成功", savedBanner));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Result<Banner>> updateBanner(@PathVariable Long id, @RequestBody Banner bannerDetails) {
        Banner banner = bannerService.getBannerById(id);
        if (banner != null) {
            banner.setTitle(bannerDetails.getTitle());
            banner.setDescription(bannerDetails.getDescription());
            banner.setImageUrl(bannerDetails.getImageUrl());
            banner.setUpdateTime(java.time.LocalDateTime.now());
            
            Banner updatedBanner = bannerService.saveBanner(banner);
            return ResponseEntity.ok(Result.success("轮播图更新成功", updatedBanner));
        } else {
            return ResponseEntity.ok(Result.error("轮播图不存在"));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Result<String>> deleteBanner(@PathVariable Long id) {
        Banner banner = bannerService.getBannerById(id);
        if (banner != null) {
            bannerService.deleteBanner(id);
            return ResponseEntity.ok(Result.success("删除成功", ""));
        } else {
            return ResponseEntity.ok(Result.error("轮播图不存在"));
        }
    }
}