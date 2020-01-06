  var socket = io();
  var $spreads_overview = $('.spreads-overview')
  var $data_updates = $('.data-updates')

  socket.on('publicView', function(clientData){
    checkSocketSession(true,socket.id)
    if ( clientData == 'loading' ){
      $data_updates.html('<table class="loading"><tbody><tr><td><div class="loading mobile-d-all">Loading</div></td></tr></tbody></table>');
    } else {
      $('.loading').remove()
      buildData(true,clientData,$data_updates,$spreads_overview,'append',function(err,updated,spreads,masterPairs){
        drawOverviewTable(masterPairs,spreads,updated,$spreads_overview,function(err){
          // ROW HIGHLIGHT ON CLICK
          setTimeout(function(){
            tableTabs()
          },400)
          rowHighlight()
          google.charts.setOnLoadCallback(function(){
            onResize(clientData)
          })
        })
      })
    }
  });//END SOCKET

  var streamRefreshCounter = 0
  socket.on('publicStream', function(clientData){
    buildData(true,clientData,$data_updates,$spreads_overview,'prepend',function(err,updated,spreads,masterPairs){
      drawOverviewTable(masterPairs,spreads,updated,$spreads_overview,function(err){
        // TABLE TABS
        setTimeout(function(){
          tableTabs()
        },400)
        rowHighlight()
        onResize(clientData)
      })
      removeLastDetailTable()
    })
    streamRefreshCounter++
    gtag('event','Page Stream Refresh',{'event_category':'View','event_label':'Home Stream Refresh','value':streamRefreshCounter})
  });//END SOCKET

  function checkSocketSession(firstLoad,id){
  if ( firstLoad == true ){
    cookie('socketID',id,{expires:365})
  } else {
    if ( cookie('socketID') != id ){
      cookie('socketID','',{expires:365})
      console.log('refresh page because socketID != id')
      var url = window.location.href
      window.location = url
    }
  }
}

  function tableTabs(){
  $('.tabs-spread-overview span').off()
  $('.tabs-spread-overview span').click(function(){
    $(this).parents('.tabs-spread-overview').find('span').removeClass('active')
    //$('.tabs-spread-overview span').removeClass('active')
    $(this).addClass('active')
    $(this).parents('.table-tabs').next('table').removeClass('d-price').removeClass('d-price2').removeClass('d-bid')
    if ( $(this).attr('data-display') == 'price' ){
      $(this).parents('.table-tabs').next('table').addClass('d-price')
    }
    if ( $(this).attr('data-display') == 'price2' ){
      $(this).parents('.table-tabs').next('table').addClass('d-price2')
    }
    if ( $(this).attr('data-display') == 'bid' ){
      $(this).parents('.table-tabs').next('table').addClass('d-bid')
    }
  })
}

  function drawOverviewTable(masterPairs,spreads,updated,$spreads_overview,cb){
  var loopcount = 0
  $spreads_overview.find('table').remove()
  masterPairs.forEach(function(pair){
    //console.log('pair',pair)
    //console.log(!pair[0].endsWith('usd') , !pair[0].endsWith('eur'))

    var pairKey = pair[0]

    // BUILD OVERVIEW TABLE
    // CLEAR HTML CAUSES RACE CONDITION, THE CODE IS FASTER THAN THE CLIENT
    setTimeout(function(){
      if ( loopcount == 0 ){
        $spreads_overview.append('<table class="d-price">\
          <thead>\
            <tr>\
            <th>Currency</th>\
            <th class="mobile-d-all">Pair</th>\
            <th class="mobile d-price d-price2">Price Spread</th>\
            <th class="mobile d-price2">Last Low Price</th>\
            <th class="mobile d-price">Low Exchange</th>\
            <th class="mobile d-price2">Last High Price</th>\
            <th class="mobile d-price">High Exchange</th>\
            <th class="mobile d-bid">Low Bid/Ask Spread</th>\
            <th class="mobile d-bid">Low B/A Exchange</th>\
            <th class="mobile d-bid">High Bid/Ask Spread</th>\
            <th class="mobile d-bid">High B/A Exchange</th>\
            </tr>\
          </thead>\
          <tbody><tr><td colspan="11" class="table-updated-at mobile-d-all">'+updated+'</td></tr>\
          </tbody>\
        </table>\
        ')
      }
      if ( spreads.pairs[pairKey] ){
        if ( spreads.pairs[pairKey].spreadLastPrice ){
          $spreads_overview.find('tbody').append('<tr class="data">\
            <td class="data-currency">'+pair[1]+'</td>\
            <td class="data-pair mobile-d-all">'+pairKey+'</td>\
            <td class="spread-overview-spread-price mobile d-price d-price2">'+spreads.pairs[pairKey].spreadLastPrice+'%</td>\
            <td class="mobile d-price2">'+spreads.pairs[pairKey].spreadLastPriceMinExchange[0]+'</td>\
            <td class="data-exchange mobile d-price">'+spreads.pairs[pairKey].spreadLastPriceMinExchange[1]+'</td>\
            <td class="mobile d-price2">'+spreads.pairs[pairKey].spreadLastPriceMaxExchange[0]+'</td>\
            <td class="data-exchange mobile d-price">'+spreads.pairs[pairKey].spreadLastPriceMaxExchange[1]+'</td>\
            <td class="spread-overview-ba mobile d-bid">'+spreads.pairs[pairKey].spreadBidAskMin[0]+'%</td>\
            <td class="data-exchange mobile d-bid">'+spreads.pairs[pairKey].spreadBidAskMin[1]+'</td>\
            <td class="spread-overview-ba mobile d-bid">'+spreads.pairs[pairKey].spreadBidAskMax[0]+'%</td>\
            <td class="data-exchange mobile d-bid">'+spreads.pairs[pairKey].spreadBidAskMax[1]+'</td>\
          </tr>')
        }
      }
      loopcount = loopcount + 1
      updatedFlash($spreads_overview)
    },40)
  })
  // ROUND FLOATS
  /*
  setTimeout(function(){
    var $spreadCells = $('.spreads-overview').find('td')
    $spreadCells.each(function(){
      var rounded = roundFloat( $(this) )
      $(this).text(rounded)
    })
  },40)*/
  cb(false)
}

  function drawDetailTables(masterPairs,pairData,spreads,timestamp,updated,$data_updates,insertOrder,cb){
  //console.log('pairData',pairData)
  if ( insertOrder == 'prepend' ){
    $data_updates.prepend('<div class="data-updates-set '+timestamp+'"></div>')
  } else {
    $data_updates.append('<div class="data-updates-set '+timestamp+'"></div>')
  }
  $data_updates_set = $('.data-updates-set.'+timestamp)
  var remaining = pairData.length
  masterPairs.forEach(function(mp){
    var pairName = mp[0]
    var pairSets = pairData[pairName]
    //console.log('pairName',pairName)
    //console.log('pairSets',pairSets)
    if ( pairSets != undefined ){
      // IF DATA DOES NOT EXIST FOR PAIR, DO NOT PRINT TABLE
      var tableHead = '<div class="table-tabs tabs-spread-overview clearfix">\
        <span class="L active" data-display="price">Price</span>\
        <span class="C" data-display="price2">Price 2</span>\
        <span class="R" data-display="bid">Bid/Ask</span>\
        </div>\
        <table class="'+timestamp+' '+pairName+' d-price">\
        <thead>\
        <tr>\
        <th>Currency</th>\
        <th class="mobile-d-all">Pair</th>\
        <th class="mobile-d-all">Exchange</th>\
        <th class="mobile d-price">Last Price</th>\
        <th class="mobile d-bid">Bid</th>\
        <th class="mobile d-bid">Ask</th>\
        <th>Bid/Ask Spread</th>\
        <th class="mobile d-price2">Last Volume</th>\
        <th class="mobile d-price">Volume 24</th>\
        </tr>\
        </thead><tbody><tr><td colspan="9" class="table-updated-at mobile-d-all">'+updated+'</td></tr></tbody></table>'
      $data_updates_set.append(tableHead)

      var $last_table = $data_updates_set.find('table.'+timestamp+'.'+pairName)

      //$('#latest-btc').find('tbody').html('')
      var eRemain = pairSets.length
      var exchangeCount = 0
      //console.log('eRemain',eRemain)
      for ( exchange in pairSets ){
        exchangeCount++
        //console.log('exchange ',exchange )
        //console.log('spreads',spreads)
        //console.log('wrapper[set][timestamp].updated',wrapper[set][timestamp].updated)
        $last_table.find('tbody').append(
            '<tr class="data '+pairSets[exchange].exchange+'">\
            <td class="data-currency">'+mp[1]+'</td>\
            <td class="data-pair mobile-d-all">'+pairName+'</td>\
            <td class="data-exchange mobile-d-all">'+pairSets[exchange].exchange+'</td>\
            <td class="data-last-price mobile d-price">'+pairSets[exchange].lastPrice+'</td>\
            <td class="data-bid mobile d-bid">'+pairSets[exchange].bid+'</td>\
            <td class="data-ask mobile d-bid">'+pairSets[exchange].ask+'</td>\
            <td class="data-bid-ask-spread">'+pairSets[exchange].bidAskSpread+'%</td>\
            <td class="mobile d-price2">'+pairSets[exchange].lastTradeVolume+'</td>\
            <td class="mobile d-price">'+pairSets[exchange].volume24+'</td>\
            </tr>')

        // LAST LOOP FOR THIS PAIR
        if ( ! --eRemain ){
          if ( exchangeCount > 1){
            // PRINT MAX BID/ASK
            //console.log('pairName', pairName, pair[exchange].exchange, timestamp)
            //console.log(spreads.pairs[pairName])
            $last_table.find('tbody').append(
                '<tr class="data-calc">\
                <td></td>\
                <td class="mobile-d-all"></td>\
                <td class="mobile-d-all"></td>\
                <td class="table-last-price-spread mobile d-price">'+spreads.pairs[pairName].spreadLastPrice+'%</td>\
                <td class="table-bid-ask-spread mobile d-bid" colspan="2">B/A Max: '+spreads.pairs[pairName].spreadBidAskMax[0]+'%</td>\
                <td></td>\
                <td class="mobile d-price2"></td>\
                <td class="mobile d-price"></td>\
                </tr>')
          }
          // HIGHLIGHT AND PRINT HIGHEST BID/ASK
          var bidAsksMax = spreads.pairs[pairName].spreadBidAskMax[0]
          var $rows = $last_table.find('.data')
          $rows.each(function(){
            var ba2 = $(this).find('.data-bid-ask-spread').text()
            if ( ba2.indexOf(bidAsksMax) > -1 ){
              $(this).find('.data-bid-ask-spread').addClass('data-bas-max').prev().addClass('data-bas-max').prev().addClass('data-bas-max')
            }
          })
          // HIGHLIGHT LOW/HIGH PRICE
          var $lastPrices = $last_table.find('.data-last-price')
          var remaining = $lastPrices.length
          $lastPrices.each(function(lp){
            if ( lp == 0 ) $(this).addClass('data-price-min');
            if ( ! --remaining ) $(this).addClass('data-price-max');
          })
          // ADD pairName CLASS TO TABLE TABS ABOVE EACH TABLE SO THAT THE CSS CAN HIDE ON CLICK OF EACH TYPE OF TAB, price || bid
          $last_table.prev().addClass(timestamp+' '+pairName)
          // ROUND FLOATS
          /*
          var $cells = $last_table.find('.data td')
          $cells.each(function(){
            var rounded = roundFloat( $(this) )
            $(this).text(rounded)
          })*/
        }
      }
      updatedFlash($last_table)
    }
  })
  cb(false)
}
function removeLastDetailTable(){
  setTimeout(function(){
    // REMOVE LAST TABLE SET
    //console.log("$('.data-updates-set').length",$('.data-updates-set').length)
    var setsLength = $('.data-updates-set').length
    $('.data-updates-set')[setsLength - 1].remove()
    //console.log('should have removed last detail table')
    //console.log("$('.data-updates-set').length",$('.data-updates-set').length)
  },200)
}

  // BUILD DATA
function buildData(isPublic,clientData,$data_updates,$spreads_overview,insertOrder,cb){
  var pairData = {}
  var spreads = {}
  var triangles = {}
  var updated = ''
  var masterPairs = clientData.masterPairs
  var exchangeList = clientData.exchangeList

  if ( insertOrder == 'append' ){
    var timeSets = clientData.data
    //console.log(insertOrder,'timeSets',timeSets)
  } else {
    var timeSets = clientData.data
    timeSets = timeSets.slice(0,1)
    //console.log(insertOrder,'timeSets',timeSets)
  }

  var remaining = timeSets.length
  timeSets.forEach(function(wrapper){
    for ( var timestamp in wrapper ){
      var blobs = wrapper[timestamp]
      var pairData = blobs.dataByPairPrice
      var spreads = blobs.spreads
      var updated = readable(timestamp)

      var triangles = blobs.triangles;
      if ( isPublic == false ){
        drawTriangles(triangles,timestamp,updated,insertOrder)
      }
      drawDetailTables(masterPairs,pairData,spreads,timestamp,updated,$data_updates,insertOrder,function(err){

      })
      if ( remaining == timeSets.length ) cb(false,updated,spreads,masterPairs);
      if ( ! --remaining ){
        //console.log("$('.alerts-select-pairs').length == 0",$('.alerts-select-pairs').length == 0)
        //if ( $('.alerts-select-pairs span').length < 2 ) drawAlerts(masterPairs,exchangeList);
      }
    }
  })
  // THE LINE BELOW ENSURES THIS ONLY PRINTS ON FIRST PAGE LOAD
  //console.log('insertOrder',insertOrder)
  if ( insertOrder == 'append' ) buildFilterByCurrency(masterPairs);
  updateDetailTables()
  drawLatestTables(clientData,masterPairs)
}
function drawLatestTables(clientData,masterPairs){
  var latestTables = [ $('#latest-btc'), $('#latest-spread-price'), $('#latest-spread-ba') ]

  for ( var timestamp in clientData.data[0] ){
    var tReadable = readable(timestamp)
    // LATEST-BTC
    var priceData = clientData.data[0][timestamp].dataByPairPrice.btc_usd
    //console.log('// LATEST BTC PRICE DATA\n',priceData)
    latestTables.forEach(function(t){
      t.find('tbody').html('')
    })
    var remaining = priceData.length
    var rowCount = 0
    priceData.forEach(function(row){
      rowCount++
      if( rowCount == 1 || rowCount == priceData.length ){
        $('#latest-btc').find('tbody').append(
          '<tr>\
          <td>'+row.exchange+'</td>\
          <td class="data-price-max">'+row.lastPrice+'</td>')
      } else {
        $('#latest-btc').find('tbody').append(
          '<tr>\
          <td>'+row.exchange+'</td>\
          <td>'+row.lastPrice+'</td>')
      }
      if ( ! --remaining ){
        // ADD TIMESTAMPS
        var rowTimeHtml = '<tr><td colspan="2" class="table-updated-at">'+tReadable+'</td></tr>'
        latestTables.forEach(function(t){
          t.find('tbody').prepend(rowTimeHtml)
        })
      }
    })
    $('#latest-btc').find('tbody').append(
        '<tr class="data-calc">\
        <td></td>\
        <td class="table-last-price-spread mobile d-price">'+clientData.data[0][timestamp].spreads.pairs.btc_usd.spreadLastPrice+'%</td>\
        </tr>')

    // LATEST BID/ASK MAX
    var baMaxPairName = ''
    var baMaxPair = clientData.data[0][timestamp].spreads.minmax.byBidAsk.max.pair
    var baMaxVal = clientData.data[0][timestamp].spreads.minmax.byBidAsk.max.val
    var baMaxExchange = clientData.data[0][timestamp].spreads.minmax.byBidAsk.max.exchange
    masterPairs.forEach(function(p){
      if ( p[0] == baMaxPair ) baMaxPairName = p[1];
    })
    $('#latest-spread-ba').find('tbody').append(
      '<tr>\
      <td class="latest-feature data-bas-max">\
      <span class="latest-val">'+baMaxVal+'%</span>\
      <span class="latest-pair">'+baMaxPairName+'</span>\
      <span class="latest-exchange">High Exchange: <strong>'+baMaxExchange+'</strong></span>\
      </td></tr>')

    // LATEST PRICE MAX
    var priceMaxPairName = ''
    var priceMaxPair = clientData.data[0][timestamp].spreads.minmax.byLastPrice.max.pair
    var priceMaxVal = clientData.data[0][timestamp].spreads.minmax.byLastPrice.max.val
    var priceMaxExchange = clientData.data[0][timestamp].spreads.minmax.byLastPrice.max.exchangeHigh
    var priceMinExchange = clientData.data[0][timestamp].spreads.minmax.byLastPrice.max.exchangeLow
    //console.log('clientData.data[0][0][timestamp].spreads.minmax.byLastPrice.max',clientData.data[0][0][timestamp].spreads.minmax.byLastPrice.max)
    masterPairs.forEach(function(p){
      if ( p[0] == priceMaxPair ) priceMaxPairName = p[1];
    })
    $('#latest-spread-price').find('tbody').append(
      '<tr>\
      <td class="latest-feature data-price-max">\
      <span class="latest-val">'+priceMaxVal+'%</span>\
      <span class="latest-pair">'+priceMaxPairName+'</span>\
      <span class="latest-exchange">Low Exchange: <strong>'+priceMinExchange+'</strong><br />High Exchange: <strong>'+priceMaxExchange+'</strong></span>\
      </td></tr>')

    // ROUND FLOATS
    /*
    var $cells = $('.home-latest').find('td')
    $cells.each(function(){
      var rounded = roundFloat( $(this) )
      $(this).text(rounded)
    })*/

    // FLASH ON UPDATE
    latestTables.forEach(function(t){
      updatedFlash(t)
    })
  }
}
function readable(t){
  t = new Date(+t)
  t = t.toString()

  if ( t.indexOf('GMT') < 0 ){
    console.log(t,'GMT not found')
    return t
  }

  var tz = t.match(/\(([A-Za-z\s].*)\)/)
  if ( tz == null ) return t;
  tz = tz[1]
  t = t.split('GMT')[0] + tz
  return t
}

  function buildFilterByCurrency(masterPairs){
  //console.log('** inside buildFilterByCurrency')
  // CLEAR OUT CONTAINERS TO PREVENT DOUBLE INSERTION ON STALE BROWSER?
  $('.filter-by-currency-select').html('')
  $('.filter-by-currency').html('')

  $('.filter-by-currency-select').append('<select class="form-control"><option value="all" selected>All Currency Pairs</options></select>')
  var remaining = masterPairs.length
  masterPairs.forEach(function(pair){
    if ( remaining == masterPairs.length ){
      $('.filter-by-currency').append('<span class="filter-by-currency-show-all">Show All<b style="display:none">all</b></span>')
    }
    $('.filter-by-currency-select').find('select').append('<option value="'+pair[0]+'">'+pair[1]+' &mdash; '+pair[0]+'</option>')
    $('.filter-by-currency').append('<span>'+pair[1]+' <b>'+pair[0]+'</b></span>')
    if ( ! --remaining){

    }
  })
  filterByCurrencyClicks()
}
function filterByCurrencyClicks(){
  // REMOVE CLICK FUNCTIONS
  $('.filter-by-currency span').off()
  // CLICK FUNCTION FOR DESKTOP
  $('.filter-by-currency span').click(function(){
    $('.filter-by-currency span').removeClass('active')
    $(this).addClass('active')
    var pairKey = $(this).find('b').text()
    cookie('pair_view',pairKey,{expires:365})
    filterDetailTables(pairKey)
    gtag('event','Click',{'event_category':'Action','event_label':'Filter - ' + pairKey})
    $('.filter-by-currency-show-all').click(function(){
      cookie('pair_view','',{expires:365})
      $('.filter-by-currency span').removeClass('active')
      $(this).addClass('active')
      $('.data-updates table').fadeIn(200)
      $('.data-updates .table-tabs').fadeIn(200)
      gtag('event','Click',{'event_category':'Action','event_label':'Filter - All Currencies'})
      return false
    })
    return false
  })
  // CLICK FUNCTION FOR MOBILE
  $('.filter-by-currency-select').find('select').change(function(){
    var pairKey = $(this).val()
    if ( pairKey == 'all' ){
      cookie('pair_view','',{expires:365})
      $('.filter-by-currency span').removeClass('active')
      $('.data-updates table').fadeIn(200)
      $('.data-updates .table-tabs').fadeIn(200)
      gtag('event','Click',{'event_category':'Action','event_label':'Filter - All Currencies'})
    } else {
      cookie('pair_view',pairKey,{expires:365})
      filterDetailTables(pairKey)
      gtag('event','Click',{'event_category':'Action','event_label':'Filter - ' + pairKey})
    }
  })
}
function updateDetailTables(){
  //console.log("cookie('pair_view')",cookie('pair_view'))
  if ( cookie('pair_view') != null && cookie('pair_view') != 'all' ){
    var pairKey = cookie('pair_view')
    filterDetailTables(pairKey)
    $('.filter-by-currency span').each(function(){
      if ( $(this).find('b').text() == pairKey ){
        $(this).addClass('active')
      }
    })
  } else {
    $('.filter-by-currency .filter-by-currency-show-all').addClass('active')
    filterDetailTables(null)
  }
}
function filterDetailTables(pairKey){
  $('.data-updates table').hide()
  $('.data-updates .table-tabs').hide()
  if ( pairKey == null || pairKey == 'all' ){
    $('.data-updates .table-tabs').fadeIn(200)
    $('.data-updates table').fadeIn(200)
  } else {
    $('.filter-by-currency-select').find('select').val(pairKey)
    $('.data-updates .table-tabs.'+pairKey).fadeIn(200)
    $('.data-updates table.'+pairKey).fadeIn(200)
  }
}

  function roundFloat(el){
  var v = el.text()
  if ( !isNaN(+v) && v != '' ){
    v = +v
    if ( v > 1 ){
      var vv = v.toFixed(4)
    } else {
      var vv = v.toFixed(7)
    }
  }
  return vv
}

  function updatedFlash(sel){
  sel.find('.table-updated-at').addClass('updated-flash')
  setTimeout(function(){
    sel.find('.table-updated-at').removeClass('updated-flash')
  },1600)
}

  function rowHighlight(){
  //console.log('****** inside rowHighlight')
  setTimeout(function(){
    $('tr').off()
    $('tr').click(function(){
      $(this).toggleClass('data-highlight')
    })
  },200)
}

  google.charts.load('current',{packages:['bar','line']})

function buildLineData(clientData){
  //console.log('clientData',clientData)

  var data = new google.visualization.DataTable();
  data.addColumn('datetime', 'Time')
  var btc_usd = clientData.btc_usd
  //console.log('btc_usd',btc_usd)

  /* THIS WAS FOR DEBUG BITMEX VALUE FOR LINE CHART
  for ( var a in btc_usd[0] ){
    btc_usd[0][a].forEach(function(e){
      if ( e.exchange == 'bitmex' ){
        console.log('*************',e.lastPrice,'********')
      }
    })
  }*/

  // DEFINE EXCHANGE NAMES
  var exchangeNamesArr = []
  for ( var firstSet in btc_usd[0] ){
    btc_usd[0][firstSet].forEach(function(exchange){
      exchangeNamesArr.push( exchange.exchange )
    })
  }
  //console.log('exchangeNamesArr',exchangeNamesArr)
  // SORT NAMES AND BUILD COLUMNS
  exchangeNamesArr.sort()
  exchangeNamesArr.forEach(function(exName){
    data.addColumn('number', exName)
  })
  // BUILD TABLE BY EXCHANGE
  var btc_usd_for_chart = []
  var counter = 0
  btc_usd.forEach(function(set){
    counter++
    for ( var t in set ){
      var timestamp = new Date(+t)
      var row = [timestamp]
      exchangeNamesArr.forEach(function(exName){
        var lp = null
        set[t].forEach(function(exchange){
          //if ( exchange.exchange == 'bitmex' && counter < 30 ) console.log('+++++++ ',exchange.lastPrice);
          //if ( exchange.exchange == 'kraken' && counter < 30 ) console.log('(((((()))))) ',exchange.lastPrice);
          if ( exName == exchange.exchange ){
            lp = exchange.lastPrice
            lp = parseFloat(lp)
            //console.log(exName,lp)
          }
        })
        row.push(lp)
        //if ( exArr.indexOf('bitmex') > -1 ) console.log('set[t]',set[t])

      })
      btc_usd_for_chart.push(row)
    }
  })
  //console.log('btc_usd_for_chart',btc_usd_for_chart)
  data.addRows(btc_usd_for_chart)

  var options = {
    chart: {
      title: '',
      subtitle: ''
    },
    hAxis: {
      title: ''
    },
    legend: {
      position:'none',
    },
    series: {
      0:{color:'#ba42ff'},
      1:{color:'#e300d1'},
      2:{color:'#76c0ff'},
      3:{color:'#570088'},
      4:{color:'#7aa862'}
    },
    vAxis: {
      format: '$#,###'
    },
    width: $('#lines-btc-usd').width(),
    height: 170
  };
  drawLines(data,options)
}
function drawLines(data,options){
  var chart = new google.charts.Line(document.getElementById('lines-btc-usd'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}

  function buildChartData(clientData){
  var firstSet = clientData.data[0]
  var spreadPairs = {}
  for ( var timestamp in firstSet ){
    spreadPairs = firstSet[timestamp].spreads.pairs
  }
  var pairArr = []
  for ( var pair in spreadPairs ){
    pairArr.push(pair)
  }
  pairArr = pairArr.sort()
  // CHART DATA - OBJECT TO BE PUSHED INTO
  var cd = [ ['Pair','Price Spread - Max','B/A Spread - Max'] ]
  // var cd = [ ['Pair', 'Price Spread %', { role: 'style' }, { role: 'annotation' }] ]
  pairArr.forEach(function(pairName){
    if ( spreadPairs[pairName].spreadLastPrice > 0 ){
      var row = []
      row.push(pairName,(spreadPairs[pairName].spreadLastPrice/100),(spreadPairs[pairName].spreadBidAskMax[0]/100))
      cd.push(row)
    }
  })

  var data = google.visualization.arrayToDataTable(cd)

  var options = {
    animation:{
      duration: 1000,
      easing: 'inAndOut',
      startup:true,
    },
    bar: { groupWidth:'94%' },
    colors: ['#1b9e77', '#d95f02', '#7570b3'],
    hAxis: {
      format: '#,###%',
      title: ''
    },
    isStacked: true,
    legend: {
      position:'none',
    },
    series: {
      0:{color:'#678e52'},
      1:{color:'#63a2ff'}
    },
    title: null,
    vAxis: {
      format: '#,###.##%',
      title: ''
    },
  };
  drawChart(data,options)
}
function drawChart(data,options){
  var chart = new google.charts.Bar(document.getElementById('columnchart_material'))
  chart.draw(data, google.charts.Bar.convertOptions(options))
}

  function onResize(clientData){
  var oR = function(){
    if ( $(window).innerWidth() > 840 ){
      $('.data-updates .table-tabs').addClass('hide')
      buildLineData(clientData)
      buildChartData(clientData)
    } else {
      $('.data-updates .table-tabs').removeClass('hide')
      // NO RESIZE BECAUSE IT HAPPENS ON TOUCH FOR SOME REASON
      //buildLineData(clientData)
    }
  }
  if ( $(window).innerWidth() > 840 ){
    oR(clientData)
  } else {
    buildLineData(clientData)
  }
  $(window).on('window:resize',function(e){
    oR(clientData)
  })
}