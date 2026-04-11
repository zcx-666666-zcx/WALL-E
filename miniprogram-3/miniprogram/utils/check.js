function check (rate,humidity,breathe,temperature,fall){
  let num = "";
  let type = false;
  if(fall == true){
    num += "跌倒，";
    type = true;
  };
  if(rate >= 170){
    num += "心率过快"
    type = true;
  };
  if(humidity >= 80){
    num += "湿度过高，";
    type = true;
  };
  if(breathe >= 30){
    num += "呼吸过快，";
    type = true;
  }
  if(temperature >= 37.1){
    num += "温度过高，";
    type = true;
  }

  return {num,type};
}

export default check;