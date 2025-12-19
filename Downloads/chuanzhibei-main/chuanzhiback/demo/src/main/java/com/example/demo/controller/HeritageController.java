package com.example.demo.controller;

import com.example.demo.entity.Heritage;
import com.example.demo.service.HeritageService;
import com.example.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/heritage")
@CrossOrigin(origins = "*")
public class HeritageController {

    @Autowired
    private HeritageService heritageService;

    @GetMapping
    public ResponseEntity<Result<List<Heritage>>> getAllHeritages() {
        List<Heritage> heritages = heritageService.getAllHeritages();
        return ResponseEntity.ok(Result.success(heritages));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Result<Heritage>> getHeritageById(@PathVariable Long id) {
        Heritage heritage = heritageService.getHeritageById(id);
        if (heritage != null) {
            return ResponseEntity.ok(Result.success(heritage));
        } else {
            return ResponseEntity.ok(Result.error("非遗项目不存在"));
        }
    }

    @PostMapping
    public ResponseEntity<Result<Heritage>> createHeritage(@RequestBody Heritage heritage) {
        Heritage savedHeritage = heritageService.saveHeritage(heritage);
        return ResponseEntity.ok(Result.success("非遗项目创建成功", savedHeritage));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Result<Heritage>> updateHeritage(@PathVariable Long id, @RequestBody Heritage heritageDetails) {
        Heritage heritage = heritageService.getHeritageById(id);
        if (heritage != null) {
            heritage.setName(heritageDetails.getName());
            heritage.setDescription(heritageDetails.getDescription());
            heritage.setImageUrl(heritageDetails.getImageUrl());
            heritage.setRegion(heritageDetails.getRegion());
            heritage.setCategory(heritageDetails.getCategory());
            heritage.setLevel(heritageDetails.getLevel());
            heritage.setUpdateTime(java.time.LocalDateTime.now());
            
            Heritage updatedHeritage = heritageService.saveHeritage(heritage);
            return ResponseEntity.ok(Result.success("非遗项目更新成功", updatedHeritage));
        } else {
            return ResponseEntity.ok(Result.error("非遗项目不存在"));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Result<String>> deleteHeritage(@PathVariable Long id) {
        Heritage heritage = heritageService.getHeritageById(id);
        if (heritage != null) {
            heritageService.deleteHeritage(id);
            return ResponseEntity.ok(Result.success("删除成功", ""));
        } else {
            return ResponseEntity.ok(Result.error("非遗项目不存在"));
        }
    }

    @GetMapping("/level/{level}")
    public ResponseEntity<Result<List<Heritage>>> getHeritagesByLevel(@PathVariable Integer level) {
        List<Heritage> heritages = heritageService.getHeritagesByLevel(level);
        return ResponseEntity.ok(Result.success(heritages));
    }

    @GetMapping("/category/{category}")
    public ResponseEntity<Result<List<Heritage>>> getHeritagesByCategory(@PathVariable String category) {
        List<Heritage> heritages = heritageService.getHeritagesByCategory(category);
        return ResponseEntity.ok(Result.success(heritages));
    }
}