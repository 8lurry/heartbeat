function showAbout(btnPass){
	document.getElementById("user-about").style.display = "block";
	document.getElementById("user-timeline").style.display = "none";
}
function showTimeline(btnPass){
	document.getElementById("user-about").style.display = "none";
	document.getElementById("user-timeline").style.display = "block";
}

function toggleSideMenu(){
	var content = document.getElementById("expanded-menu");
	if (content.style.display == "block"){
		content.style.display = "none";
	}
	else {
		content.style.display = "block";
	}
	content.addEventListener('click', function(e){
		e.stopPropagation();
	});
	document.addEventListener('click', function(e){
		if (content.style.display === "block" && e.target !== document.getElementById("nav-menu-icon") && e.target !== document.getElementById("nav-menu")){
			content.style.display = "none";
		}
	});
}

function toggleSearchFilterButton(){
	var sFilterButton = document.getElementById("drop-filter");
	sFilterButton.style.display = "block";
	document.addEventListener('click', function(e){
		if (sFilterButton.style.display === "block" && e.target !== document.getElementById("search-main") && e.target !== sFilterButton.getElementsByTagName("i")[0]) {
			sFilterButton.style.display = "none";
		}
	});
}
function toggleSearchFilter(){
	var sFilter = document.getElementById("search-filter"), 
		doctor = document.getElementById("id_doctor"),
		schedule = document.getElementById("id_schedule"),
		facility = document.getElementById("id_facility");
	var doc_ini = doctor.checked, sche_ini = schedule.checked, fac_ini = facility.checked;
	if (sFilter.style.display === "block"){
		sFilter.style.display = "none";
	} else {
		sFilter.style.display = "block";
	}
	sFilter.addEventListener('click', function(e){
		e.stopPropagation();
	});
	document.addEventListener('click', function(e){
		if (sFilter.style.display === "block" && e.target !== sFilter && e.target !== document.getElementById('search-main') && e.target !== document.getElementById("search-filter-button")){
			sFilter.style.display = "none";
		}
	});
	document.getElementById("filter-ok").addEventListener('click', function(e){
		sFilter.style.display = "none";
	});
	document.getElementById("filter--ok").addEventListener("click", function(e){
		doctor.checked = doc_ini;
		schedule.checked = sche_ini;
		facility.checked = fac_ini;
		sFilter.style.display = "none";
	});
	document.getElementById("search-main").addEventListener("input", function(){
		if (sFilter.style.display === "block"){
			sFilter.style.display = "none";
		}
	});
}

function toggleAccountsOption(){
	var accounts = document.getElementById("accounts-dropdown"),
		up = document.getElementById("accounts-up"),
		down = document.getElementById("accounts-down");
	if (accounts.style.display === "block"){
		accounts.style.display = "none";
		up.style.display = "none";
		down.style.display = "block";
	} else {
		accounts.style.display = "block";
		up.style.display = "block";
		down.style.display = "none";
	}
}
function validateUsername(){
	$("#id_username").change(function(){
		var username = $(this).val();
		var html = document.getElementById("signup-form").getElementsByTagName("li")[0];
		$.ajax({
			url: "/ajax/validate_username/",
			data: {"username": username},
			dataType: "json",
			success: function(data){
				if (typeof(html.getElementsByTagName("p")[0]) == "undefined" && data.is_taken){
					html.innerHTML += "<p style='font-size: small;'>Sorry, This username is taken! Pick another one.</p>";
				}
				html.getElementsByTagName("input")[0].addEventListener('click', function(){
					if ( typeof(html.getElementsByTagName("p")[0]) !== "undefined"){
						html.getElementsByTagName("p")[0].remove();
					}
					validateUsername();
				});
			}
		});
	});
}
document.getElementById("search-main").addEventListener('input', function(){
	var search = document.getElementById("search-main"),
		doctor = document.getElementById("id_doctor").checked,
		facility = document.getElementById("id_facility").checked,
		schedule = document.getElementById("id_schedule").checked;
	$.ajax({
		url: "/ajax/query_search/",
		data: {
			'search': search.value,
			'doctor': doctor,
			'schedule': schedule,
			'facility': facility
		},
		dataType: 'json',
		success: function(data){
			var html =  document.getElementById("srch-main-suggestion"),
				li = html.getElementsByTagName("li");
			if (data["queryset"].length > 0){
				html.style.display = "block";
				for (i = 0; i < data["queryset"].length; i++){
					html.innerHTML += "<li>" + data["queryset"][i] + "</li>"
				}
				if (li != "undefined"){
					for (i = 0; i < li.length; i++) {
						if ( li[i].textContent in data["queryset"]){
							//do nothing
						} else {
							li[i].remove();
						}
					}
					html.addEventListener("click", function(e){
						search.value = e.target.textContent;
					});
				}
			} else {
				if (li != "undefined"){
					for (i = 0; i < li.length; i++){
						li[i].remove();
					}
					if (html.style.display === "block"){
						html.style.display = "none";
					}
				}
			}
			html.addEventListener('click', function(e){
				e.stopPropagation();
			});
			document.addEventListener('click', function(e){
				if (html.style.display === "block" && e.target != html && e.target != document.getElementById("search-main")){
					html.style.display = "none";
				}
			});
		}
	});
});
function srchEmpty(){
	if (document.getElementById("search-main").value == ""){
		return false;
	}
}