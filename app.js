var app = angular.module('plunker', []);
app.directive('cellLocation', function() {
    return {
        templateUrl: 'cellLocation.html',
        controller: function($scope){
            $scope.allComponents = {}; // a dict of object cellComponents
            $scope.updateSelection = function(sel){
                $scope.cellComponent = sel;
                if (!$scope.allComponents[sel.id])
                    $scope.allComponents[sel.id] = sel;
                $scope.allComponents[sel.id].selected = !$scope.allComponents[sel.id].selected;
            };
        },
        link: function(scope, elem, attrs){
            var svg = d3.select("#cell");
            svg.selectAll('.col').selectAll('path')
              .transition()
                .duration(200).style("opacity",0);

            console.log(scope.allComponents);
            var innerCol = svg.selectAll('.col')
            .on('mouseover',function(){
                 svg.selectAll('#'+d3.select(this).attr("id")).selectAll('path')
                 .transition()
                    .duration(200).style("opacity",1);
            })
            .on('mouseleave', function(){
               if (!scope.allComponents[d3.select(this).attr("id")] ||
                    !scope.allComponents[d3.select(this).attr("id")].selected)
                   svg.selectAll('#'+d3.select(this).attr("id")).selectAll('path')
                   .transition()
                      .duration(200)
                      .style("opacity",0);
               else
                  svg.selectAll('#'+d3.select(this).attr("id")).selectAll('path')
                  .transition()
                      .duration(200)
                      .style("opacity",1);
            })
            .on('click',function(d){
                var cellComponent = {
                    id : d3.select(this).attr("id"),
                    class:  d3.select(this).attr("class"),
                    title : d3.select(this).attr("title"),
                    pval_1: d3.select(this).attr("min-pval"),
                    pval_2: d3.select(this).attr("init-pval"),
                    pval_3: d3.select(this).attr("min-pval-children"),
                    children: d3.select(this).attr("children")
                };
                scope.$apply(scope.updateSelection(cellComponent));
            });

            var tonCol = svg.selectAll('.ton').on('click',function(d){
                var cellComponent = {
                    id : d3.select(this).attr("id"),
                    class:  d3.select(this).attr("class"),
                    title : d3.select(this).attr("title"),
                    pval_1 : d3.select(this).attr("min-pval"),
                    pval_2: d3.select(this).attr("init-pval"),
                    pval_3: d3.select(this).attr("min-pval-children"),
                    children: d3.select(this).attr("children")
                };
                scope.$apply(scope.updateSelection(cellComponent));
            });
            // scope.$apply(function(){
              // console.log(innerCol);
              // scope.cellComponent = {id:innerCol.length};
            // });
            $scope.watch('allComponents', function(newData){
                console.log(newData);
                svg.selectAll('.col').selectAll('path')
                .transition()
                    .duration(200).style("opacity",0);
            })
        }
    };
});
app.controller('MainCtrl', function($scope) {});