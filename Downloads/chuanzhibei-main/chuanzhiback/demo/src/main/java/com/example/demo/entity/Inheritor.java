package com.example.demo.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "inheritor")
public class Inheritor extends BaseEntity {
    private String name;
    private String skill;
    private String description;
    private String imageUrl;
    private String level; // 国家级传承人, 省级传承人等
    
    // Constructors
    public Inheritor() {
        super();
    }
    
    public Inheritor(String name, String skill, String description, String imageUrl, String level) {
        this.name = name;
        this.skill = skill;
        this.description = description;
        this.imageUrl = imageUrl;
        this.level = level;
    }
    
    // Getters and Setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getSkill() {
        return skill;
    }
    
    public void setSkill(String skill) {
        this.skill = skill;
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
    
    public String getLevel() {
        return level;
    }
    
    public void setLevel(String level) {
        this.level = level;
    }
}