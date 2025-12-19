package com.example.demo.service;

import com.example.demo.entity.ArExperience;
import com.example.demo.repository.ArExperienceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ArExperienceService {
    
    @Autowired
    private ArExperienceRepository arExperienceRepository;
    
    public List<ArExperience> getAllArExperiences() {
        return arExperienceRepository.findAll();
    }
    
    public List<ArExperience> getHotArExperiences() {
        return arExperienceRepository.findByIsHot(true);
    }
    
    public ArExperience getArExperienceById(Long id) {
        return arExperienceRepository.findById(id).orElse(null);
    }
    
    public ArExperience saveArExperience(ArExperience arExperience) {
        return arExperienceRepository.save(arExperience);
    }
    
    public void deleteArExperience(Long id) {
        arExperienceRepository.deleteById(id);
    }
}