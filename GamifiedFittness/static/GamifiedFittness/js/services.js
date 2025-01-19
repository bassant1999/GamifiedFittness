const Chalenge = {
    async List (name) {
      var strUrl = "{% url 'list_chalenges' %}";
  
      let fetchResult = await fetch(strUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name:name })
        });
      let myData = await fetchResult.json();
      return myData;
    },
    async Add (objActivity) {
      var strUrl = 'activities/add';
  
      let fetchResult = await fetch(strUrl, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ objActivity: objActivity })
        });
      let myData = await fetchResult.json();
      return myData;
    },
  }
    
    export  {Activity};