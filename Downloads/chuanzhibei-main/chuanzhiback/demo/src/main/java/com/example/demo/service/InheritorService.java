package com.example.demo.service;

import com.example.demo.entity.Inheritor;
import com.example.demo.repository.InheritorRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class InheritorService {
    
    @Autowired
    private InheritorRepository inheritorRepository;
    
    public List<Inheritor> getAllInheritors() {
        return inheritorRepository.findAll();
    }
    
    public List<Inheritor> getInheritorsByLevel(String level) {
        return inheritorRepository.findByLevel(level);
    }
    
    public List<Inheritor> getInheritorsBySkill(String skill) {
        return inheritorRepository.findBySkill(skill);
    }
    
    public Inheritor getInheritorById(Long id) {
        return inheritorRepository.findById(id).orElse(null);
    }
    
    public Inheritor saveInheritor(Inheritor inheritor) {
        return inheritorRepository.save(inheritor);
    }
    
    public void deleteInheritor(Long id) {
        inheritorRepository.deleteById(id);
    }
}