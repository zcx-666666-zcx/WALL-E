package com.example.demo.service;

import com.example.demo.entity.Heritage;
import com.example.demo.repository.HeritageRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class HeritageService {
    
    @Autowired
    private HeritageRepository heritageRepository;
    
    public List<Heritage> getAllHeritages() {
        return heritageRepository.findAll();
    }
    
    public List<Heritage> getHeritagesByLevel(Integer level) {
        return heritageRepository.findByLevel(level);
    }
    
    public List<Heritage> getHeritagesByCategory(String category) {
        return heritageRepository.findByCategory(category);
    }
    
    public List<Heritage> getRecommendedHeritages() {
        return heritageRepository.findTop4ByOrderByIdAsc();
    }
    
    public Heritage getHeritageById(Long id) {
        return heritageRepository.findById(id).orElse(null);
    }
    
    public Heritage saveHeritage(Heritage heritage) {
        return heritageRepository.save(heritage);
    }
    
    public void deleteHeritage(Long id) {
        heritageRepository.deleteById(id);
    }
}