const root = document.getElementById("app");

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

const StatusSpinner = {
    view: function (vnode) {
        return m(".d-flex.flex-column.justify-content-center.align-items-center", [
            m(".spinner-border.text-primary", {'style': "width: 4rem; height: 4rem", "role": "status"}),
            m("h5.mt-4", vnode.attrs.status.charAt(0).toUpperCase() + vnode.attrs.status.slice(1))
        ])

    }
}

const HeroSection = {
    view: function () {
        return m(
            'section',
            [
                m('nav.d-flex.justify-content-flex-start', {style: "height: 100px;"}, [
                    m('a.navbar-brand', {href: '#', style: "height: 100%"}, [
                        m('img', {
                            src: '/static/img/logo.png',
                            alt: 'Logo',
                            style: "padding: 15px 0 0 0; height: 100%;"
                        })
                    ])
                ]),
                m('.row', {style: 'margin-top: 50px'}, [
                    m('.col-lg-6', [
                        m('.d-flex.flex-column.align-items-start', [
                            m('h1.font-weight-bold', {style: "margin-bottom: 60px; font-size: 3.5rem"}, 'Unleashing the Power of Advanced ECG Analysis'),
                            m('h5', {style: "margin-bottom: 60px; line-height: 2.2rem"}, 'Harness the potential of cutting-edge AI technology to revolutionize cardiac health diagnosis and treatment.'),
                            m('a.btn.btn-primary.mt-auto[href="#training-section"]', {style: 'padding: 15px 35px; font-size: 1.5rem'}, 'Explore, Train, Diagnose!')
                        ])
                    ]),
                    m('.d-flex.justify-content-center.align-items-center.col-lg-6', {}, [
                        m('img', {src: '/static/img/hero-heart.png', alt: 'Heart Image', style: 'height: 420px;'})
                    ])
                ])
            ]);
    }
};


const ChartComponent = {
    oninit: function (vnode) {
        this.chartData = JSON.parse(vnode.attrs.chartData);
    },
    oncreate: function (vnode) {
        Plotly.newPlot(vnode.dom, this.chartData.data, this.chartData.layout);
    },
    view: function () {
        return m('div')
    }
};

const TrainingService = {
    sessionId: null,
    trainingStatus: "initialized",
    trainingMetrics: {},
    chartsData: {},
    showResults: false,

    runTraining: function (data) {
        FileUpload.file = null;
        m.request({
            method: "POST",
            url: "/api/modelling/session/",
            body: data,
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            }
        }).then(response => {
            TrainingService.sessionId = response.id;
            TrainingService.showResults = true;

            TrainingService.trainingStatus = "initialized";
            TrainingService.trainingMetrics = {};
            TrainingService.chartsData = {};

            TrainingService.checkStatus();
        }).catch(error => {
            console.log(error.response);
            TrainingService.errors = error.response;
        });


    },
    checkStatus: function () {
        if (TrainingService.sessionId === null) return;

        clearInterval(TrainingService.interval);

        TrainingService.interval = setInterval(() => {
            m.request({
                method: "GET",
                url: "/api/modelling/session/" + TrainingService.sessionId,
            }).then(response => {
                TrainingService.trainingStatus = response.status;

                if (response.status === "done") {
                    TrainingService.chartsData = JSON.parse(response.charts);
                    delete response.charts;

                    TrainingService.trainingMetrics = response;
                }
            });

            if (TrainingService.trainingStatus === "done") {
                clearInterval(TrainingService.interval);
            }
        }, 2000);
    },
};

const TrainingSetup = {
    algorithmParams: {
        'knn': {
            'readable': 'K Nearest Neighbors',
            'parameters': [
                {name: 'n_neighbors', default: '5', readable: 'Neighbors number', required: false},
                {
                    name: 'weights',
                    default: 'uniform',
                    readable: 'Weights',
                    choices: ['uniform', 'distance'],
                    required: false
                },
                {
                    name: 'algorithm',
                    default: 'auto',
                    readable: 'Algorithm',
                    choices: ['auto', 'ball_tree', 'kd_tree', 'brute'],
                    required: false
                },
            ]
        },
        'svc': {
            'readable': "Support Vector Machine",
            'parameters': [
                {name: 'C', default: '1.0', readable: 'Penalty Parameter C', required: false},
                {
                    name: 'kernel',
                    default: 'rbf',
                    readable: 'Kernel Type',
                    choices: ['linear', 'poly', 'rbf', 'sigmoid'],
                    required: false
                },
                {name: 'degree', default: '3', readable: 'Degree of the Polynomial Kernel Function', required: false},
            ]
        },
        'random_forest': {
            'readable': 'Random Forest',
            'parameters': [
                {name: 'n_estimators', default: '100', readable: 'Number of estimators', required: false},
                {
                    name: 'criterion',
                    default: 'gini',
                    readable: 'Criterion',
                    choices: ['gini', 'entropy'],
                    required: false
                },
                {name: 'max_depth', default: null, readable: 'The Maximum Depth of the Tree', required: false},
            ]
        },
    },
    inputs: {
        general: {
            alphabet_size: 100,
            word2vec_vector_size: 100,
            algorithm: ''
        },
        algorithmConfig: {}
    },
    showResults: false,
    view: function () {
        const chosenAlgorithmParams = this.inputs.general.algorithm
            ? this.algorithmParams[this.inputs.general.algorithm].parameters
            : [];

        this.errors = TrainingService.errors || {};

        return m("form.d-flex.flex-column.justify-content-center", [
            m('h3', 'Setup'),
            m(".form-row.mt-4", [
                m(".col", [
                    m("label.h6", "Alphabet size"),
                    m("input.form-control[type=text][placeholder='Enter a value'][required]", {
                        name: "alphabet_size",
                        value: this.inputs.general.alphabet_size,
                        oninput: (e) => {
                            this.inputs.general.alphabet_size = e.target.value;
                            if (this.errors.alphabet_size) {
                                delete this.errors.alphabet_size;
                            }
                        }
                    }),
                    this.errors.alphabet_size && m(".text-danger.mt-1", this.errors.alphabet_size[0])
                ]),
                m(".col", [
                    m("label.h6", "Word2Vec vector size"),
                    m("input.form-control[type=text][placeholder='Enter a value'][required]", {
                        name: "word2vec_vector_size",
                        value: this.inputs.general.word2vec_vector_size,
                        oninput: (e) => {
                            this.inputs.general.word2vec_vector_size = e.target.value;
                        }
                    }),
                ]),
                m(".col", [
                    m("label.h6", "Algorithm"),
                    m("select.form-control", {
                            name: "algorithm",
                            value: this.inputs.general.algorithm,
                            oninput: (e) => {
                                this.inputs.general.algorithm = e.target.value;
                                if (!this.inputs.algorithmConfig[e.target.value]) {
                                    this.inputs.algorithmConfig[e.target.value] = this.algorithmParams[e.target.value].parameters.reduce((params, param) => {
                                        params[param.name] = param.default || null;
                                        return params;
                                    }, {});
                                }
                                if (this.errors.algorithm) {
                                    delete this.errors.algorithm;
                                }
                            },
                        }, [
                            m("option", {
                                value: '',
                                selected: this.inputs.general.algorithm === '',
                                disabled: true
                            }, 'Select an Algorithm'),
                            ...Object.keys(this.algorithmParams).map(algorithm =>
                                m("option", {
                                    value: algorithm,
                                    selected: this.inputs.general.algorithm === algorithm
                                }, this.algorithmParams[algorithm].readable)
                            ),


                        ],
                    ), this.errors.algorithm && m(".text-danger.mt-1", this.errors.algorithm[0])
                ])
            ]),
            this.inputs.general.algorithm && m(".form-row.mt-4", chosenAlgorithmParams.map((param) =>
                m(".col", [
                    m("label.h6", param.readable),
                    param.choices
                        ? m("select.form-control", {
                                name: param.name,
                                value: (this.inputs.algorithmConfig[this.inputs.general.algorithm] && this.inputs.algorithmConfig[this.inputs.general.algorithm][param.name]) || null,
                                required: param.required,
                                onchange: (e) => {
                                    this.inputs.algorithmConfig[this.inputs.general.algorithm][param.name] = e.target.value;
                                }
                            },
                            param.choices.map(choice =>
                                m("option", {value: choice}, choice)
                            )
                        )
                        : m("input.form-control[type=text][placeholder='Enter a value']", {
                            name: param.name,
                            value: (this.inputs.algorithmConfig[this.inputs.general.algorithm] && this.inputs.algorithmConfig[this.inputs.general.algorithm][param.name]) || null,
                            required: param.required,
                            onchange: (e) => {
                                this.inputs.algorithmConfig[this.inputs.general.algorithm][param.name] = e.target.value
                            }
                        })
                ])
            )),
            m("button.btn.btn-primary[type=submit].mt-5.", {
                style: 'padding: 15px 0; font-size: 1.5rem',
                onclick: (event) => {
                    event.preventDefault();

                    // Fill in 'word2vec_vector_size' if it's missing
                    if (!this.inputs.general.word2vec_vector_size) {
                        this.inputs.general.word2vec_vector_size = 100;
                    }

                    // Get the algorithm parameters

                    if (this.inputs.general.algorithm) {
                        const algorithmParameters = this.algorithmParams[this.inputs.general.algorithm].parameters;

                        // Fill in missing input values with their defaults
                        for (let param of algorithmParameters) {
                            const input = this.inputs.algorithmConfig[this.inputs.general.algorithm][param.name];
                            if (input === undefined || input === null || input === '') {
                                this.inputs.algorithmConfig[this.inputs.general.algorithm][param.name] = param.default;
                            }
                        }

                    }

                    // Proceed with running the training session
                    const data = {
                        general_params: this.inputs.general,
                        algorithm_params: this.inputs.algorithmConfig[this.inputs.general.algorithm]
                    };
                    TrainingService.runTraining(data);

                }
            }, "Run")
        ])
    }
}


const TrainingResult = {
    view: function () {
        if (TrainingService.trainingStatus !== "done") {
            return m(StatusSpinner, {status: TrainingService.trainingStatus})
        }

        return m('.d-flex.flex-column.justify-content-center', [
            m('h3', 'Results'),
            m(".row.mt-4", [
                m(".col-4", [
                    m(".card", [
                        m(".card-body", [
                            m("h5.card-title", "Training accuracy"),
                            m("p.card-text", TrainingService.trainingMetrics['train_accuracy'])
                        ])
                    ])
                ]),
                m(".col-4", [
                    m(".card", [
                        m(".card-body", [
                            m("h5.card-title", "Precision"),
                            m("p.card-text", TrainingService.trainingMetrics['precision'])
                        ])
                    ])
                ]),
                m(".col-4", [
                    m(".card", [
                        m(".card-body", [
                            m("h5.card-title", "F1 score"),
                            m("p.card-text", TrainingService.trainingMetrics['f1_score'])
                        ])
                    ])
                ])
            ]),
            m(".row.mt-4", [
                m(".col-4", [
                    m(".card", [
                        m(".card-body", [
                            m("h5.card-title", "Testing accuracy"),
                            m("p.card-text", TrainingService.trainingMetrics['test_accuracy'])
                        ])
                    ])
                ]),
                m(".col-4", [
                    m(".card", [
                        m(".card-body", [
                            m("h5.card-title", "Recall"),
                            m("p.card-text", TrainingService.trainingMetrics['recall'])
                        ])
                    ])
                ]),
                m(".col-4", [
                    m(".card", [
                        m(".card-body", [
                            m("h5.card-title", "Silhouette score"),
                            m("p.card-text", TrainingService.trainingMetrics['silhouette_score'])
                        ])
                    ])
                ])
            ]),
            m(".row.mt-4", [
                m(".col-6", [
                    m(".card.h-100", [
                        m(".card-body", [
                            m("h5.card-title", "Confusion matrix"),
                            m(".w-100", [m(ChartComponent, {chartData: TrainingService.chartsData['confusion_matrix']})])
                        ])
                    ])
                ]),
                m(".col-6", [
                    m(".card.h-100", [
                        m(".card-body", [
                            m("h5.card-title", "TSNE of QRS complexes"),
                            m(".w-100", [m(ChartComponent, {chartData: TrainingService.chartsData['tsne']['qrs']})])
                        ])
                    ])
                ]),
            ]),
            m(".row.mt-4", [
                m(".col-6", [
                    m(".card.h-100", [
                        m(".card-body", [
                            m("h5.card-title", "TSNE of P waves"),
                            m(".w-100", [m(ChartComponent, {chartData: TrainingService.chartsData['tsne']['p']})])
                        ])
                    ])
                ]),
                m(".col-6", [
                    m(".card.h-100", [
                        m(".card-body", [
                            m("h5.card-title", "TSNE of T waves"),
                            m(".w-100", [m(ChartComponent, {chartData: TrainingService.chartsData['tsne']['t']})])
                        ])
                    ])
                ]),
            ]),
        ])
    }
}

const TrainingSection = {
    view: function () {
        return m(
            'section.d-flex.flex-column.justify-content-flex-start#training-section', {style: 'margin-top: 150px'},
            [
                m('h1.font-weight-bold', {style: 'font-size: 3.5rem'}, 'Modelling'),
                m('h5.mt-3', 'Play with hyper-parameters to train the best algorithm'),
                m('.mt-5', [m(TrainingSetup)]),
                TrainingService.showResults && m('.mt-5', [m(TrainingResult)])
            ]
        )
    }
}

const FileUpload = {
    file: null,

    view: function () {
        return m(".row", [
            m(".col-sm", [
                m(".card", [
                    m(".card-body", [
                        m("h5.card-title", "Upload file"),
                        FileUpload.file
                            ? [
                                m("p.card-text", FileUpload.file.name + " (" + FileUpload.file.size + " bytes)"),
                                m("button.btn.btn-danger", {
                                    onclick: function () {
                                        FileUpload.file = null;
                                        AnalysisService.showResults = false;
                                    }
                                }, "X"),
                            ]
                            : [
                                m("p.card-text", "Drag your file here or click to upload."),
                                m(".border.border-primary", {
                                    style: {
                                        height: "200px",
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        flexDirection: "column",
                                        cursor: "pointer"
                                    },
                                    onclick: function () {
                                        this.previousElementSibling.click();
                                    },
                                    ondragover: function (e) {
                                        e.preventDefault();
                                    },
                                    ondrop: function (e) {
                                        e.preventDefault();
                                        var file = e.dataTransfer.files[0];
                                        if (file && /\.(csv|xlsx)$/i.test(file.name)) {
                                            if (file.size <= 5 * 1024 * 1024) {
                                                FileUpload.file = file;
                                                m.redraw();
                                            } else {
                                                alert("File too large. Please upload a file smaller than 5MB.");
                                            }
                                        } else {
                                            alert("Invalid file. Please upload a CSV or XLSX file.");
                                        }
                                    }
                                }, "Drop file here")
                            ]
                    ])
                ])
            ])
        ]);
    }
};


const AnalysisService = {
    chartsData: {},
    tableData: {},
    showResults: false,
    analysisStatus: null,

    runAnalysis: function (data) {
        AnalysisService.analysisStatus = 'running';
        m.request({
            method: "POST",
            url: "/api/analysis/session/",
            body: data,
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        }).then(response => {
            AnalysisService.showResults = true;
            AnalysisService.chartsData = response['charts'];
            AnalysisService.tableData = response['table'];
            AnalysisService.analysisStatus = 'done';

        }).catch(error => {
            AnalysisService.errors = error.response;
        });

    },
};

const AnalysisSetup = {
    showResults: false,
    fs: 360,
    view: function () {
        this.errors = AnalysisService.errors || {};

        return m(
            '.d-flex.flex-column.justify-content-flex-start',
            [
                m('h3', 'Setup'),
                m('.mt-4', [m(FileUpload)]),

                FileUpload.file && m(".d-flex.flex-column.mt-4", [
                    m("label.h6", "Sampling frequency (fs)"),
                    m("input.form-control[type=text][placeholder='Enter a value']", {
                        value: AnalysisSetup.fs,
                        oninput: (e) => {
                            AnalysisSetup.fs = e.target.value;
                        },
                    }),
                    this.errors.fs && m(".text-danger.mt-1", this.errors.fs[0])
                ]),

                FileUpload.file && m("button.btn.btn-primary[type=submit].mt-5.", {
                    style: 'padding: 15px 0; font-size: 1.5rem',
                    onclick: function (event) {
                        event.preventDefault();

                        AnalysisSetup.fs = AnalysisSetup.fs || 360;

                        const formData = new FormData();
                        formData.append('ecg_file', FileUpload.file);
                        formData.append('fs', AnalysisSetup.fs);
                        formData.append('training_session_id', TrainingService.sessionId);

                        AnalysisService.runAnalysis(formData)
                    }
                }, "Run")
            ]
        )
    }
}

const AnalysisResult = {
    view: function () {
        if (AnalysisService.analysisStatus !== "done") {
            return m(StatusSpinner, {status: 'analyzing'})
        }

        console.log(AnalysisService.chartsData)
        return m(
            '.d-flex.flex-column.justify-content-flex-start',
            [
                m('h3', 'Result'),
                m(".row.mt-4", [
                        m(".col-12", [
                            m(".card", [
                                m(".card-body", [
                                    m("h5.card-title.mb-3", "Analyzed ECG"),
                                    m(".w-100", [m(ChartComponent, {chartData: AnalysisService.chartsData['line']})])
                                ])
                            ]),
                            m(".card.mt-3", [
                                m(".card-body", [
                                    m("h5.card-title.mb-3", "Heartbeats"),
                                    m("table.table", [
                                        m("thead", [
                                            m("tr", [
                                                m("th", "Number"),
                                                m("th", "Predicted Label"),
                                                m("th", "Word"),
                                                m("th", "Word Vector")
                                            ])
                                        ]),
                                        m("tbody",
                                            AnalysisService.tableData.map(function (heartbeat) {
                                                let vectorPreview = heartbeat["word_vector"].slice(0, 2).toString() + "..."; // Trim the vector for the preview
                                                return m('tr', [
                                                    m('td', heartbeat["index"]),
                                                    m('td', heartbeat["predicted_label"]),
                                                    m('td', heartbeat["word"]),
                                                    m('td[data-toggle=tooltip][data-placement=right][title=' + JSON.stringify(heartbeat["word_vector"]) + ']', vectorPreview), // Show full vector in the tooltip
                                                ]);
                                            })
                                        ),
                                    ])
                                ])
                            ])
                        ])
                    ]
                )
            ]
        )
    }
}

const AnalysisSection = {
    view: function () {
        return m(
            'section.d-flex.flex-column.justify-content-flex-start', {style: 'margin-top: 150px'},
            [
                m('h1.font-weight-bold', {style: 'font-size: 3.5rem'}, 'Analysis'),
                m('h5.mt-3', 'Run the prepared model on your own data'),

                m('.mt-5', [m(AnalysisSetup)]),
                AnalysisService.showResults && m('.mt-5', [m(AnalysisResult)])
            ]
        )
    }
}


const Main = {
    view: function () {
        return m(
            '.container.mb-5',
            m(HeroSection),
            m(TrainingSection),
            TrainingService.trainingStatus === 'done' && m('.mt-5', [m(AnalysisSection)])
        )
    }
}

m.route(
    root,
    "/",
    {
        "/": Main,
    }
)