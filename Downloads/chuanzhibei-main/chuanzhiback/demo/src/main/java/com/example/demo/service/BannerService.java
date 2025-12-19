package com.example.demo.service;

import com.example.demo.entity.Banner;
import com.example.demo.repository.BannerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BannerService {
    
    @Autowired
    private BannerRepository bannerRepository;
    
    public List<Banner> getAllBanners() {
        return bannerRepository.findAllByOrderByCreateTimeDesc();
    }
    
    public Banner getBannerById(Long id) {
        return bannerRepository.findById(id).orElse(null);
    }
    
    public Banner saveBanner(Banner banner) {
        return bannerRepository.save(banner);
    }
    
    public void deleteBanner(Long id) {
        bannerRepository.deleteById(id);
    }
}