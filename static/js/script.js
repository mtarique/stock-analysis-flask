$(document).ready(function() {
    // When the form is submitted, prevent the default form submission
    $('#stockForm').submit(function(event) {
        event.preventDefault();  // Prevent the default form submission
    
        var symbol = $('#symbol').val();
        var period = $('#period').val();

        // Make an AJAX request to the '/analyze' route
        $.ajax({
            url: '/analyze',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'symbol': symbol,
                'period': period
            }),
            beforeSend: () => $('.spinner-container').removeClass('d-none'),
            complete: () => $('.spinner-container').addClass('d-none'),
            success: function(response) {
                if (response.error) {
                    let $errorElem = `
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <strong>Oops! </strong>
                            ${response.error}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `; 

                    $('#stockResult').html($errorElem);
                } else {
                    console.log(response)
                    let resultElem = ``; 
                    let currencySymbol = ''; 
                    let $infoElem = ``; 
                    
                    if(response.stock_info) {
                        let stockInfo = response.stock_info;
                        let currentPrice = parseFloat(stockInfo.currentPrice); 
                        currencySymbol = getCurrencySymbol(stockInfo.currency); 

                        let recommendationColor = response.prediction == 'BUY' ? "text-bg-success" : "text-bg-danger"; 
                        let priceChange = response.price_change || 0; 
                        let priceChangePct = response.price_change_pct || 0; 

                        let priceChangeClass = priceChange >= 0 ? "text-success" : "text-danger";
                        let priceChangePctClass = priceChangePct >= 0 ? "text-success" : "text-danger";
                        
                        let stockName = stockInfo.longName ? `${stockInfo.longName} (${symbol})` : symbol; 
                        $infoElem = `
                            <div class="card-header d-flex justify-content-between align-items-center bg-white"> 
                                <div>
                                    <h6 class="card-title">${stockName}</h6>
                                
                                    <p class="mb-0">
                                        <span class="me-1 h3">${currencySymbol}${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                        <span class="me-1 h6 ${priceChangeClass}">${formatNumber(priceChange.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))}</span>
                                        <span class="h6 ${priceChangePctClass}">(${formatNumber(priceChangePct.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))}%)</span>
                                    </p>
                                    <small>${response.close_datetime}</small>
                                </div>
                                
                                <span class="badge ${recommendationColor}">${response.prediction}</span>
                            </div>
                        `;  
                    }

                    // Populate the stock data table
                    var stockData = response.stock_data_table;
                    let $historicalTable = ``;
                    if(stockData) {
                        $historicalTable = `
                        <div class="table-responsive">
                            <table id="stockData" class="display table table-sm table-bordered table-hover">
                                <thead class="table-light">
                                    <tr>
                                        <th class="text-center align-middle">Date</th>
                                        <th class="text-center align-middle">Open</th>
                                        <th class="text-center align-middle">High</th>
                                        <th class="text-center align-middle">Low</th>
                                        <th class="text-center align-middle">Close</th>
                                        <th class="text-center align-middle">Volume</th>
                                    </tr>
                                </thead>
                                <tbody>
                        `; 

                        stockData.forEach(function(row) {
                            $historicalTable += `
                                <tr>
                                    <td class="text-center align-middle" data-sort="${moment(row.Date).format('YYYY-MM-DD')}"> ${moment(row.Date).format('DD MMM YYYY')} </td>
                                    <td class="text-end align-middle"> ${currencySymbol+row.Open.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} </td>
                                    <td class="text-end align-middle"> ${currencySymbol+row.High.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} </td>
                                    <td class="text-end align-middle"> ${currencySymbol+row.Low.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} </td>
                                    <td class="text-end align-middle"> ${currencySymbol+row.Close.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} </td>
                                    <td class="text-end align-middle"> ${row.Volume} </td>
                                </tr>
                            `; 
                        });

                        $historicalTable += `</tbody></table></div>`; 
                    }

                    let $stockNewsElem = `<div class="row gx-4 mt-3">`; 
                    
                    if(response.stock_news) {
                        const stockNews = response.stock_news;

                        stockNews.forEach((article, index) => {
                            if(article.title) {
                                // Create a new Bootstrap 5 card
                                $stockNewsElem += `
                                    <div class="col-md-3 mb-3">
                                        <div class="card ">
                                            <img src="${article.thumbnail.resolutions[0].url}" class="card-img-top" alt="Article Image">
                                            <div class="card-body">
                                                <h6 class="card-title">${article.title}</h6>
                                            </div>
                                            <div class="card-footer bg-white d-grid border-top-0">
                                                <a href="${article.link}" class="btn btn-primary btn-sm" target="_blank">Read More...</a>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            }
                        }) 
                    }

                    $stockNewsElem += `</div>`;

                    resultElem += `
                        <div class="card rounded-0- shadow mb-3">
                            ${$infoElem}
                            <div class="card-body pt-0 pb-3 px-3">
                                <ul class="nav nav-underline" id="myTab" role="tablist">
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button" role="tab" aria-controls="overview" aria-selected="true">Overview</button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="historical-data-tab" data-bs-toggle="tab" data-bs-target="#historical-data" type="button" role="tab" aria-controls="historical-data" aria-selected="false">Historical Data</button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="news-tab" data-bs-toggle="tab" data-bs-target="#news" type="button" role="tab" aria-controls="news" aria-selected="false">News</button>
                                    </li>
                                </ul>
                                <div class="tab-content" id="myTabContent">
                                    <div class="tab-pane fade show active" id="overview" role="tabpanel" aria-labelledby="overview-tab">
                                        ${response.chart_html || "Chart could not be generated"}
                                        <br>
                                        ${response.line_chart || "Line chart could not be generated"}
                                    </div>
                                    <div class="tab-pane fade" id="historical-data" role="tabpanel" aria-labelledby="historical-data-tab">
                                        <div class="d-flex justify-content-between align-items-center mb-3"> 
                                            <h5 class="mb-0"></h5>
                                            <button class="btn btn-sm btn-primary buttons-csv" id="customExportCSV">Download CSV</button>
                                        </div
                                        ${$historicalTable}
                                    </div>
                                    <div class="tab-pane fade" id="news" role="tabpanel" aria-labelledby="news-tab">
                                        ${$stockNewsElem}
                                    </div>
                                </div>
                            
                            </div>
                        </div>
                    `; 
                    
                    $('#stockResult').html(resultElem);

                    let dtHistoricalData = $('#stockData').DataTable({
                        paging: false,
                        scrollY: 400, 
                        order: [[0, 'desc']],
                        scrollX: true, // Enables horizontal scrolling
                        fixedColumns: {
                            leftColumns: 1 // Number of columns to fix on the left side
                        }, 
                        dom: 'Brt', // B for Buttons, f for search, r for processing, t for table, i for info, p for pagination
                        buttons: [
                            {
                                extend: 'csvHtml5',
                                title: 'Data export',
                                exportOptions: {
                                    columns: ':visible'
                                },
                                filename: 'Exported_Data',
                                customize: function(csv) {
                                    return csv; // Optional: custom logic to modify CSV data
                                }
                            },
                            {
                                extend: 'excelHtml5',
                                title: 'Data export',
                                exportOptions: {
                                    columns: ':visible'
                                },
                                filename: 'Exported_Data',
                                customize: function(xlsx) {
                                    // Optional: custom logic to modify Excel data
                                }
                            }
                        ]
                    }); 

                    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
                        $('#stockData').DataTable().columns.adjust().draw();
                    });

                    // Attach the event listener for tab show to handle head column width
                    document.querySelectorAll('#myTab button[data-bs-toggle="tab"]').forEach((tab) => {
                        tab.addEventListener('shown.bs.tab', (event) => {
                            if (dtHistoricalData) {
                                dtHistoricalData.columns.adjust().draw();
                            }
                        });
                    });

                    // Bind custom button click events to the DataTable export functions
                    $('#customExportCSV').on('click', function() {
                        dtHistoricalData.button('.buttons-csv').trigger();
                    });

                    $('#customExportExcel').on('click', function() {
                        dtHistoricalData.button('.buttons-excel').trigger();
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error(error);
                let $errorElem = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <strong>Oops! </strong>
                        ${xhr.status}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `; 

                $('#error').html($errorElem);
            }
        });

        function getCurrencySymbol(currencyCode) {
            return (0).toLocaleString('en', {
                style: 'currency',
                currency: currencyCode,
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).replace(/\d/g, '').trim();
        }

        function formatNumber(number) {
            if (number > 0) {
                return '+' + number;  // Adds "+" for positive numbers
            } else if (number < 0) {
                return number;  // Keeps the "-" for negative numbers
            } else {
                return number.toString();  // Returns 0 as is
            }
        }

    });
})