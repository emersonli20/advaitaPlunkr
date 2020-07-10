app.directive('cellLocation', function() {
  return {	
	link: function(scope, elem, attrs){	
		var cyMaScale = d3.interpolateLab('cyan', 'magenta');
		var el = document.createElement('html');
		el.innerHTML = $(document).ready(function()
			  {
				$.get('cellLocation.html', function(html_string){
				  alert(html_string);
			  }, 'html');
			  });
		var components = el.querySelectorAll("g[title] > path[style]");
		components.forEach(function(component){
			component.style.fill = cyMaScale(1);
		})
		scope.newCellLocation = el.innerHTML;
		},
	template: '<div ng-include="newCellLocation"></div>',
	}
});

