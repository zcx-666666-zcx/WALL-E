-- Insert sample data for the intangible heritage database

-- Sample users
INSERT INTO user (username, password, nickname, email) VALUES 
('admin', '$2a$10$w9ziBssO.EJmBEdrh4zBnOQ/FHNY72gju/9uQjcJ18Xk48Evh1FlW', '管理员', 'admin@example.com'),
('testuser', '$2a$10$w9ziBssO.EJmBEdrh4zBnOQ/FHNY72gju/9uQjcJ18Xk48Evh1FlW', '测试用户', 'testuser@example.com')
ON DUPLICATE KEY UPDATE username=username;

-- Sample news
INSERT INTO news (title, description, image_url, date) VALUES 
('2024年全国非遗文化节即将开幕', '一年一度的全国非物质文化遗产节将在北京举行，届时将有来自全国各地的非遗项目参展。', 'http://localhost:8001/uploads/news/festival.jpg', '2024-05-20'),
('传统工艺创新大赛圆满落幕', '为期三个月的传统工艺创新大赛在杭州落下帷幕，共有来自全国各地的200余件作品参赛。', 'http://localhost:8001/uploads/news/competition.jpg', '2024-05-18'),
('非遗传承人走进校园', '多位非遗传承人走进北京大学，为学生们带来了一场精彩的文化盛宴。', 'http://localhost:8001/uploads/news/campus.jpg', '2024-05-15'),
('数字化保护助力非遗传承', '随着科技的发展，越来越多的非遗项目通过数字化手段得到保护和传播。', 'http://localhost:8001/uploads/news/digital.jpg', '2024-05-10')
ON DUPLICATE KEY UPDATE title=title;

-- Sample heritage items
INSERT INTO heritage (name, description, image_url, detail_image_url, region, category, level) VALUES 
('昆曲', '昆曲是中国最古老的戏曲声腔、剧种，被称为"百戏之祖"。', 'http://localhost:8001/uploads/heritage/kunqu.jpg', 'http://localhost:8001/uploads/heritage/kunqu_detail.jpg', '江苏昆山', '戏曲', 1),
('苏绣', '苏绣是中国传统刺绣工艺之一，以精细、雅致著称。', 'http://localhost:8001/uploads/heritage/suxiu.jpg', 'http://localhost:8001/uploads/heritage/suxiu_detail.jpg', '江苏苏州', '传统技艺', 1),
('太极拳', '太极拳是一种内外兼修、刚柔并济的中国传统拳术。', 'http://localhost:8001/uploads/heritage/taiji.jpg', 'http://localhost:8001/uploads/heritage/taiji_detail.jpg', '河南焦作', '传统体育', 1),
('端午节', '端午节是中国首个入选世界非遗的节日。', 'http://localhost:8001/uploads/heritage/dragonboat.jpg', 'http://localhost:8001/uploads/heritage/dragonboat_detail.jpg', '全国', '民俗', 1)
ON DUPLICATE KEY UPDATE name=name;

-- Sample inheritors
INSERT INTO inheritor (name, skill, description, avatar, level, experience_years) VALUES 
('王师傅', '苏绣', '江苏省工艺美术大师，从事苏绣创作30余年', 'http://localhost:8001/uploads/inheritor/master1.jpg', '国家级', 30),
('李老师', '昆曲', '著名昆曲表演艺术家，国家一级演员', 'http://localhost:8001/uploads/inheritor/master2.jpg', '国家级', 40)
ON DUPLICATE KEY UPDATE name=name;

-- Sample AR experiences
INSERT INTO ar_experience (name, description, image_url, model_url, instructions, is_hot) VALUES 
('青铜器复原体验', '通过AR技术还原古代青铜器的制作过程', 'http://localhost:8001/uploads/ar/bronze.jpg', 'http://localhost:8001/models/bronze.glb', '请确保环境光线充足，并保持设备稳定', TRUE),
('古画复活体验', '利用AR技术让古画中的场景动起来', 'http://localhost:8001/uploads/ar/painting.jpg', 'http://localhost:8001/models/painting.glb', '请将摄像头对准平面区域，避免强光直射', TRUE)
ON DUPLICATE KEY UPDATE name=name;

-- Sample banners for homepage
INSERT INTO banner (title, description, image_url) VALUES 
('2024年全国非遗文化节', '传承经典，弘扬中华文化', 'http://localhost:8001/uploads/banners_index/banner_1.jpg'),
('陶瓷技艺入选世界非遗名录', '景德镇陶瓷烧制技艺列入人类非遗代表作名录', 'http://localhost:8001/uploads/banners_index/banner_2.jpg'),
('剪纸艺术进校园活动', '全国范围内开展剪纸艺术进校园系列活动', 'http://localhost:8001/uploads/banners_index/banner_3.jpg'),
('传统工艺创新大赛', '展现新时代工匠精神', 'http://localhost:8001/uploads/banners_index/banner_4.jpg'),
('非遗文化宣传周', '让更多人了解和热爱传统文化', 'http://localhost:8001/uploads/banners_index/banner_5.jpg')
ON DUPLICATE KEY UPDATE title=title;