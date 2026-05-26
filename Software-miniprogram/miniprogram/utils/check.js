function check(rate, humidity, breathe, temperature, fall) {
  let num = "";
  let type = false;

  if (fall === true) {
    num += "跌倒";
    type = true;
  }
  if (rate >= 170) {
    if (num) num += "，";
    num += "心率过快";
    type = true;
  }
  if (rate <= 59 && rate >= 0 && rate !== -1) {
    if (num) num += "，";
    num += "心率过慢";
    type = true;
  }
  if (humidity >= 80) {
    if (num) num += "，";
    num += "湿度过高";
    type = true;
  }
  if (humidity <= 39 && humidity >= 0 && humidity !== -1) {
    if (num) num += "，";
    num += "湿度过低";
    type = true;
  }
  if (breathe >= 30) {
    if (num) num += "，";
    num += "呼吸过快";
    type = true;
  }
  if (breathe <= 11 && breathe >= 0 && breathe !== -1) {
    if (num) num += "，";
    num += "呼吸过慢";
    type = true;
  }
  if (temperature >= 37.1) {
    if (num) num += "，";
    num += "体温过高";
    type = true;
  }
  if (temperature <= 35.8 && temperature > 0 && temperature !== -1) {
    if (num) num += "，";
    num += "体温过低";
    type = true;
  }

  return { num, type };
}

export default check;
