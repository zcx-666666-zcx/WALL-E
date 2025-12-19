package com.example.demo.service;

import com.example.demo.entity.News;
import com.example.demo.repository.NewsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class NewsService {
    
    @Autowired
    private NewsRepository newsRepository;
    
    public List<News> getAllNews() {
        return newsRepository.findAll();
    }
    
    public List<News> getRecentNews() {
        LocalDate oneWeekAgo = LocalDate.now().minusWeeks(1);
        return newsRepository.findByDateAfter(oneWeekAgo);
    }
    
    public List<News> searchNews(String keyword) {
        return newsRepository.findByTitleContainingIgnoreCase(keyword);
    }
    
    public News getNewsById(Long id) {
        return newsRepository.findById(id).orElse(null);
    }
    
    public News saveNews(News news) {
        return newsRepository.save(news);
    }
    
    public void deleteNews(Long id) {
        newsRepository.deleteById(id);
    }
}