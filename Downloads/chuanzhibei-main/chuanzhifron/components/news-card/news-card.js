Component({
  properties: {
    news: {
      type: Object,
      value: {}
    }
  },
  
  methods: {
    onTap: function() {
      this.triggerEvent('tap', this.data.news);
    },
    
    onFavTap: function() {
      this.triggerEvent('favtap', this.data.news);
    }
  }
});