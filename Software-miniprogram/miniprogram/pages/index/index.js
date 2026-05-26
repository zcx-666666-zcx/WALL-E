const { getStaticUrl } = require('../../utils/config.js');

Page({
  data: {
    image_ip1: '',
    image_ip2: '',
    image_ip3: '',
    image_ip4: ''
  },

  onLoad() {
    this.setData({
      image_ip1: getStaticUrl('/images/index_container1.png'),
      image_ip2: getStaticUrl('/images/index_picture.png'),
      image_ip3: getStaticUrl('/images/index_picture2.png'),
      image_ip4: getStaticUrl('/images/index_picture3.png')
    })
  }
})
