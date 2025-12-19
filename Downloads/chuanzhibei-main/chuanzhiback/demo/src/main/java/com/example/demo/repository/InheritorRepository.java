package com.example.demo.repository;

import com.example.demo.entity.Inheritor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InheritorRepository extends JpaRepository<Inheritor, Long> {
    List<Inheritor> findByLevel(String level);
    List<Inheritor> findBySkill(String skill);
}