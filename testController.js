app.controller('MainCtrl', function($scope, $http) {
  var cyMaScale = d3.interpolateLab('cyan', 'magenta');
  $scope.values = ["melanoma", "breast_cancer"];
  $scope.value = $scope.values[0];
  $(document).ready(function(){
  $http.get('plunker_inputs_' + $scope.value + '.json').success(function(data){
    var components = data;
    console.log(components);
		$scope.colorMaps = {};
    var logs = [];
    for (var i=0; i < components.length; i++){
      console.log(components[i].Title);
      //{components[i].Title + 'Color': compColor}
      var compColor;
      if (components[i].interpolate === null){
        compColor = 'white';
      }
      else {
        var x = components[i].interpolate;
        compColor = cyMaScale(x);
        logs[logs.length] = components[i].log_min_pval;
      }
      console.log(compColor);
      $scope.colorMaps[components[i].Title + 'Color'] = compColor;
    }
    $scope.maxLog = Math.max(...logs).toFixed(2);
    });
  });
});