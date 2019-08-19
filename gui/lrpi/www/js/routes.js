angular.module('app.routes', [])

.config(function($stateProvider, $urlRouterProvider) {

  // Ionic uses AngularUI Router which uses the concept of states
  // Learn more here: https://github.com/angular-ui/ui-router
  // Set up the various states which the app can be in.
  // Each state's controller can be found in controllers.js
  $stateProvider
    

      .state('tabsController.settings', {
    url: '/settings',
    views: {
      'tab1': {
        templateUrl: 'templates/settings.html',
        controller: 'settingsCtrl'
      }
    }
  })

  .state('tabsController.play', {
    url: '/play',
    views: {
      'tab2': {
        templateUrl: 'templates/play.html',
        controller: 'playCtrl'
      }
    }
  })

  .state('tabsController.test', {
    url: '/test',
    views: {
      'tab3': {
        templateUrl: 'templates/test.html',
        controller: 'testCtrl'
      }
    }
  })

  .state('tabsController.about', {
    url: '/about',
    views: {
      'tab6': {
        templateUrl: 'templates/about.html',
        controller: 'aboutCtrl'
      }
    }
  })

  .state('tabsController.liveRecord', {
    url: '/record',
    views: {
      'tab4': {
        templateUrl: 'templates/liveRecord.html',
        controller: 'liveRecordCtrl'
      }
    }
  })

  .state('tabsController.lushroomConvert', {
    url: '/convert',
    views: {
      'tab5': {
        templateUrl: 'templates/lushroomConvert.html',
        controller: 'lushroomConvertCtrl'
      }
    }
  })

  .state('tabsController', {
    url: '/tabs',
    templateUrl: 'templates/tabsController.html',
    abstract:true
  })

$urlRouterProvider.otherwise('/tabs/about')


});