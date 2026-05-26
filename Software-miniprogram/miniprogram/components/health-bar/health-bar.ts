Component({
  data: {
    visible: false,
    rate: -1, humidity: -1, breathe: -1, temp: -1, fall: null as boolean | null,
    rateStatus: 'idle', tempStatus: 'idle', humidStatus: 'idle',
    breatheStatus: 'idle', fallStatus: 'idle',
    rateFlash: false,
    lastRate: null as number | null,
  },

  lifetimes: {
    attached() {
      this.updateFromGlobal();
      this._timer = setInterval(() => {
        this.updateFromGlobal();
      }, 2000);
    },
    detached() {
      if (this._timer) clearInterval(this._timer);
    }
  },

  methods: {
    updateFromGlobal() {
      const g = getApp().globalData;
      const rate = Number(g.RATE);
      const humidity = Number(g.HUMIDITY);
      const breathe = Number(g.BREATHE);
      const temp = Number(g.TEMPERATURE);
      const fall = g.FALL;

      const rateStatus   = isNaN(rate) || rate === -1 ? 'idle' : this.classifyRate(rate);
      const tempStatus   = isNaN(temp) || temp === -1 ? 'idle' : this.classifyTemp(temp);
      const humidStatus  = isNaN(humidity) || humidity === -1 ? 'idle' : this.classifyHumidity(humidity);
      const breatheStatus = isNaN(breathe) || breathe === -1 ? 'idle' : this.classifyBreathe(breathe);
      const fallStatus   = fall === true ? 'danger' : fall === false ? 'normal' : 'idle';

      const updates: any = {
        visible: true,
        rate: isNaN(rate) ? -1 : rate,
        humidity: isNaN(humidity) ? -1 : humidity,
        breathe: isNaN(breathe) ? -1 : breathe,
        temp: isNaN(temp) ? -1 : temp,
        fall: fall === true ? true : fall === false ? false : null,
        rateStatus, tempStatus, humidStatus, breatheStatus, fallStatus,
      };

      if (this.data.lastRate !== null && this.data.lastRate !== -1 && rate !== this.data.lastRate) {
        updates.rateFlash = true;
        setTimeout(() => this.setData({ rateFlash: false }), 600);
      }
      this.data.lastRate = rate;

      this.setData(updates);
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

    onTapNavigate() {
      wx.navigateTo({ url: '/pages/healthy/healthy' });
    }
  }
});
