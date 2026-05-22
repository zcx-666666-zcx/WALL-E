// pages/contact/contact.ts
Page({
  data: {
    contacts: [] as { id: number; name: string; phone: string }[],
  },

  onLoad() {
    this.loadContacts();
  },

  onShow() {
    this.loadContacts();
  },

  loadContacts() {
    const stored = wx.getStorageSync('emergency_contacts') || [];
    this.setData({ contacts: stored });
  },

  addContact() {
    wx.showModal({
      title: '添加联系人',
      editable: true,
      placeholderText: '请输入联系人姓名',
      success: (res) => {
        if (res.confirm && res.content) {
          const name = res.content.trim();
          wx.showModal({
            title: '输入电话',
            editable: true,
            placeholderText: '请输入电话号码',
            success: (res2) => {
              if (res2.confirm && res2.content) {
                const contacts = this.data.contacts;
                contacts.push({
                  id: Date.now(),
                  name,
                  phone: res2.content.trim(),
                });
                this.setData({ contacts });
                wx.setStorageSync('emergency_contacts', contacts);
                wx.showToast({ title: '添加成功', icon: 'success' });
              }
            }
          });
        }
      }
    });
  },

  callContact(e: any) {
    const phone = e.currentTarget.dataset.phone;
    if (phone) {
      wx.makePhoneCall({ phoneNumber: phone });
    }
  },
});
