package com.example.demo.controller;

import com.example.demo.entity.Banner;
import com.example.demo.entity.Heritage;
import com.example.demo.entity.News;
import com.example.demo.service.BannerService;
import com.example.demo.service.HeritageService;
import com.example.demo.service.NewsService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/home")
@CrossOrigin(origins = "*")
public class HomeController {

    @Autowired
    private BannerService bannerService;
    
    @Autowired
    private NewsService newsService;
    
    @Autowired
    private HeritageService heritageService;

    /**
     * 获取首页数据
     * 包括轮播图、推荐项目和最新新闻
     */
    @GetMapping("/data")
    public ResponseEntity<Result<Map<String, Object>>> getHomeData() {
        Map<String, Object> homeData = new HashMap<>();
        
        // 获取轮播图数据
        List<Banner> banners = bannerService.getAllBanners();
        homeData.put("banners", banners);
        
        // 获取推荐非遗项目
        List<Heritage> recommendHeritages = heritageService.getRecommendedHeritages();
        homeData.put("recommendHeritages", recommendHeritages);
        
        // 获取最新新闻
        List<News> recentNews = newsService.getRecentNews();
        homeData.put("recentNews", recentNews);
        
        return ResponseEntity.ok(Result.success(homeData));
    }
}