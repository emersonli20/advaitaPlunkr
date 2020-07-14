app.controller('MainCtrl', function($scope) {
  var cyMaScale = d3.interpolateLab('cyan', 'magenta');
  $scope.values = [ "melanoma", "breast_cancer"];
  $scope.value = $scope.values[0];
  var jsonStr = $.getJSON('plunker_inputs_' + $scope.value + '.json');
  var components = json.parse(jsonStr);
  $scope.colorMaps = {};
  for (var i; i < components.length; i++){
    //{components[i].title + 'Color': compColor}
    var compColor;
    if (components[i].interpolate === null){
      compColor = rgb(255, 255, 255);
    }
    else {
      var x = components[i].interpolate;
      compColor = cyMaScale(x);
    }
    $scope.colorMaps[components[i].title + 'Color'] = compColor;
  }
});