package com.example.demo.repository;

import com.example.demo.entity.ArExperience;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ArExperienceRepository extends JpaRepository<ArExperience, Long> {
    List<ArExperience> findByIsHot(Boolean isHot);
}