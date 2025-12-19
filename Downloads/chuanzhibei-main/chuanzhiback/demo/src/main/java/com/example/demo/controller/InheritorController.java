package com.example.demo.controller;

import com.example.demo.entity.Inheritor;
import com.example.demo.service.InheritorService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/inheritor")
@CrossOrigin(origins = "*")
public class InheritorController {

    @Autowired
    private InheritorService inheritorService;

    @GetMapping
    public ResponseEntity<Result<List<Inheritor>>> getAllInheritors() {
        List<Inheritor> inheritors = inheritorService.getAllInheritors();
        return ResponseEntity.ok(Result.success(inheritors));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Result<Inheritor>> getInheritorById(@PathVariable Long id) {
        Inheritor inheritor = inheritorService.getInheritorById(id);
        if (inheritor != null) {
            return ResponseEntity.ok(Result.success(inheritor));
        } else {
            return ResponseEntity.ok(Result.error("传承人不存在"));
        }
    }

    @PostMapping
    public ResponseEntity<Result<Inheritor>> createInheritor(@RequestBody Inheritor inheritor) {
        Inheritor savedInheritor = inheritorService.saveInheritor(inheritor);
        return ResponseEntity.ok(Result.success("传承人创建成功", savedInheritor));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Result<Inheritor>> updateInheritor(@PathVariable Long id, @RequestBody Inheritor inheritorDetails) {
        Inheritor inheritor = inheritorService.getInheritorById(id);
        if (inheritor != null) {
            inheritor.setName(inheritorDetails.getName());
            inheritor.setSkill(inheritorDetails.getSkill());
            inheritor.setDescription(inheritorDetails.getDescription());
            inheritor.setImageUrl(inheritorDetails.getImageUrl());
            inheritor.setLevel(inheritorDetails.getLevel());
            inheritor.setUpdateTime(java.time.LocalDateTime.now());
            
            Inheritor updatedInheritor = inheritorService.saveInheritor(inheritor);
            return ResponseEntity.ok(Result.success("传承人更新成功", updatedInheritor));
        } else {
            return ResponseEntity.ok(Result.error("传承人不存在"));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Result<String>> deleteInheritor(@PathVariable Long id) {
        Inheritor inheritor = inheritorService.getInheritorById(id);
        if (inheritor != null) {
            inheritorService.deleteInheritor(id);
            return ResponseEntity.ok(Result.success("删除成功", ""));
        } else {
            return ResponseEntity.ok(Result.error("传承人不存在"));
        }
    }

    @GetMapping("/level/{level}")
    public ResponseEntity<Result<List<Inheritor>>> getInheritorsByLevel(@PathVariable String level) {
        List<Inheritor> inheritors = inheritorService.getInheritorsByLevel(level);
        return ResponseEntity.ok(Result.success(inheritors));
    }

    @GetMapping("/skill/{skill}")
    public ResponseEntity<Result<List<Inheritor>>> getInheritorsBySkill(@PathVariable String skill) {
        List<Inheritor> inheritors = inheritorService.getInheritorsBySkill(skill);
        return ResponseEntity.ok(Result.success(inheritors));
    }
}