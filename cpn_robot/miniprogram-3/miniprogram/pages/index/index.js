Page({
  data:{
    image_ip1: '',
    image_ip2: '',
    image_ip3: '',
    image_ip4: ''
  },

  onload(){
    this.setData({
      image_ip1:'http://localhost:8080/images/index_container1.png',
      image_ip2:'http://localhost:8080/images/index_picture.png',
      image_ip3:'http://localhost:8080/images/index_picture2.png',
      image_ip4:'http://localhost:8080/images/index_picture3.png'
    })
  }


})
