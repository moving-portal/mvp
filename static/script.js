"use strict";

dawaAutocomplete.dawaAutocomplete(document.getElementById("adresse"), {
  select: function (selected) {
	let adr = selected.data;
  console.log(selected);
  console.log(selected.data.adgangsadresseid);

  var results = document.querySelector("#results");
  results.innerHTML = "";

  fetch(`/providers?dawa=${adr.id}&street=${adr.vejnavn}&number=${adr.husnr}&postalcode=${adr.postnr}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      
      var template = document.querySelector("#provider");
          
      for (var key in data) {
        var clone = template.content.cloneNode(true);
        clone.querySelector(".provider-logo").src = "static/media/" + data[key].provider + ".png";
        clone.querySelector(".provider-link").href = data[key].link;
        clone.querySelector(".provider").textContent = data[key].provider;
        clone.querySelector(".description").textContent = data[key].description;
        clone.querySelector(".price").textContent = data[key].price + " kr./md";
        clone.querySelector(".speed").textContent = data[key].downstream + "/" + data[key].upstream + " Mbit";
        results.appendChild(clone);
      }
    });
  },
});
