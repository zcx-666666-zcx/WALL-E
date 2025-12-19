package com.example.demo.controller;

import com.example.demo.entity.ArExperience;
import com.example.demo.service.ArExperienceService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/ar-experiences")
@CrossOrigin(origins = "*")
public class ArExperienceController {

    @Autowired
    private ArExperienceService arExperienceService;

    @GetMapping
    public ResponseEntity<Result<List<ArExperience>>> getAllArExperiences() {
        List<ArExperience> arExperiences = arExperienceService.getAllArExperiences();
        return ResponseEntity.ok(Result.success(arExperiences));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Result<ArExperience>> getArExperienceById(@PathVariable Long id) {
        ArExperience arExperience = arExperienceService.getArExperienceById(id);
        if (arExperience != null) {
            return ResponseEntity.ok(Result.success(arExperience));
        } else {
            return ResponseEntity.ok(Result.error("AR体验项目不存在"));
        }
    }

    @PostMapping
    public ResponseEntity<Result<ArExperience>> createArExperience(@RequestBody ArExperience arExperience) {
        ArExperience savedArExperience = arExperienceService.saveArExperience(arExperience);
        return ResponseEntity.ok(Result.success("AR体验项目创建成功", savedArExperience));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Result<ArExperience>> updateArExperience(@PathVariable Long id, @RequestBody ArExperience arExperienceDetails) {
        ArExperience arExperience = arExperienceService.getArExperienceById(id);
        if (arExperience != null) {
            arExperience.setName(arExperienceDetails.getName());
            arExperience.setDescription(arExperienceDetails.getDescription());
            arExperience.setImageUrl(arExperienceDetails.getImageUrl());
            arExperience.setIsHot(arExperienceDetails.getIsHot());
            arExperience.setUpdateTime(java.time.LocalDateTime.now());
            
            ArExperience updatedArExperience = arExperienceService.saveArExperience(arExperience);
            return ResponseEntity.ok(Result.success("AR体验项目更新成功", updatedArExperience));
        } else {
            return ResponseEntity.ok(Result.error("AR体验项目不存在"));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Result<String>> deleteArExperience(@PathVariable Long id) {
        ArExperience arExperience = arExperienceService.getArExperienceById(id);
        if (arExperience != null) {
            arExperienceService.deleteArExperience(id);
            return ResponseEntity.ok(Result.success("删除成功", ""));
        } else {
            return ResponseEntity.ok(Result.error("AR体验项目不存在"));
        }
    }

    @GetMapping("/hot")
    public ResponseEntity<Result<List<ArExperience>>> getHotArExperiences() {
        List<ArExperience> hotArExperiences = arExperienceService.getHotArExperiences();
        return ResponseEntity.ok(Result.success(hotArExperiences));
    }
}