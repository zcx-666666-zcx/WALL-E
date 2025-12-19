package com.example.demo.repository;

import com.example.demo.entity.Heritage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface HeritageRepository extends JpaRepository<Heritage, Long> {
    List<Heritage> findByLevel(Integer level);
    List<Heritage> findByCategory(String category);
    List<Heritage> findTop4ByOrderByIdAsc();
}