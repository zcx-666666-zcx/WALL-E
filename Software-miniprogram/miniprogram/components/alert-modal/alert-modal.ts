Component({
  data: {
    show: false,
    dismissing: false,
    snoozedText: '',
    alertText: '',
    rate: -1, humidity: -1, breathe: -1, temperature: -1,
    rateStatus: 'idle', tempStatus: 'idle', humidStatus: 'idle', breatheStatus: 'idle',
  },

  lifetimes: {
    attached() {
      this.checkAlert();
      this._timer = setInterval(() => {
        this.checkAlert();
      }, 2000);
    },
    detached() {
      if (this._timer) clearInterval(this._timer);
    }
  },

  methods: {
    checkAlert() {
      const g = getApp().globalData;
      const rate = Number(g.RATE);
      const humidity = Number(g.HUMIDITY);
      const breathe = Number(g.BREATHE);
      const temperature = Number(g.TEMPERATURE);
      const fall = g.FALL;

      let text = '';
      if (fall === true) text += '跌倒';
      if (!isNaN(rate) && rate !== -1 && rate >= 170) { if (text) text += '，'; text += '心率过快'; }
      if (!isNaN(rate) && rate !== -1 && rate <= 59) { if (text) text += '，'; text += '心率过慢'; }
      if (!isNaN(humidity) && humidity !== -1 && humidity >= 80) { if (text) text += '，'; text += '湿度过高'; }
      if (!isNaN(humidity) && humidity !== -1 && humidity <= 39) { if (text) text += '，'; text += '湿度过低'; }
      if (!isNaN(breathe) && breathe !== -1 && breathe >= 30) { if (text) text += '，'; text += '呼吸过快'; }
      if (!isNaN(breathe) && breathe !== -1 && breathe <= 11) { if (text) text += '，'; text += '呼吸过慢'; }
      if (!isNaN(temperature) && temperature !== -1 && temperature >= 37.1) { if (text) text += '，'; text += '体温过高'; }
      if (!isNaN(temperature) && temperature !== -1 && temperature <= 35.8) { if (text) text += '，'; text += '体温过低'; }

      if (text.length === 0) {
        if (this.data.snoozedText) this.setData({ snoozedText: '' });
        return;
      }

      if (text === this.data.snoozedText) return;

      const rateVal = isNaN(rate) ? -1 : rate;
      const humidityVal = isNaN(humidity) ? -1 : humidity;
      const breatheVal = isNaN(breathe) ? -1 : breathe;
      const tempVal = isNaN(temperature) ? -1 : temperature;

      this.setData({
        show: true,
        dismissing: false,
        alertText: text,
        rate: rateVal, humidity: humidityVal,
        breathe: breatheVal, temperature: tempVal,
        rateStatus: rateVal === -1 ? 'idle' : this.classifyRate(rateVal),
        tempStatus: tempVal === -1 ? 'idle' : this.classifyTemp(tempVal),
        humidStatus: humidityVal === -1 ? 'idle' : this.classifyHumidity(humidityVal),
        breatheStatus: breatheVal === -1 ? 'idle' : this.classifyBreathe(breatheVal),
      });
    },

    classifyRate(v: number): string {
      if (v >= 170) return 'danger';
      if (v >= 120 || v <= 59) return 'warn';
      return 'normal';
    },
    classifyTemp(v: number): string {
      if (v >= 37.1) return 'danger';
      if (v <= 35.8) return 'warn';
      return 'normal';
    },
    classifyHumidity(v: number): string {
      if (v >= 80) return 'danger';
      if (v <= 39) return 'warn';
      return 'normal';
    },
    classifyBreathe(v: number): string {
      if (v >= 30) return 'danger';
      if (v <= 11) return 'warn';
      return 'normal';
    },

    preventTouchMove() { return; },

    onDismiss() {
      this.setData({ dismissing: true });
      setTimeout(() => {
        this.setData({ show: false, dismissing: false });
      }, 250);
    },

    onSnooze() {
      this.setData({ snoozedText: this.data.alertText });
      this.onDismiss();
    },

    onViewDetail() {
      wx.navigateTo({ url: '/pages/healthy/healthy' });
    }
  }
});
