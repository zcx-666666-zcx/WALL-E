package com.example.demo.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "ar_experience")
public class ArExperience extends BaseEntity {
    private String name;
    private String description;
    private String imageUrl;
    private Boolean isHot;
    
    // Constructors
    public ArExperience() {
        super();
    }
    
    public ArExperience(String name, String description, String imageUrl, Boolean isHot) {
        this.name = name;
        this.description = description;
        this.imageUrl = imageUrl;
        this.isHot = isHot;
    }
    
    // Getters and Setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public String getImageUrl() {
        return imageUrl;
    }
    
    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }
    
    public Boolean getIsHot() {
        return isHot;
    }
    
    public void setIsHot(Boolean isHot) {
        this.isHot = isHot;
    }
}