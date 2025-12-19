package com.example.demo.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "heritage")
public class Heritage extends BaseEntity {
    private String name;
    private String description;
    private String imageUrl;
    private String region;
    private String category;
    private Integer level; // 1: 国家级, 2: 省级
    
    // Constructors
    public Heritage() {
        super();
    }
    
    public Heritage(String name, String description, String imageUrl, String region, String category, Integer level) {
        this.name = name;
        this.description = description;
        this.imageUrl = imageUrl;
        this.region = region;
        this.category = category;
        this.level = level;
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
    
    public String getRegion() {
        return region;
    }
    
    public void setRegion(String region) {
        this.region = region;
    }
    
    public String getCategory() {
        return category;
    }
    
    public void setCategory(String category) {
        this.category = category;
    }
    
    public Integer getLevel() {
        return level;
    }
    
    public void setLevel(Integer level) {
        this.level = level;
    }
}