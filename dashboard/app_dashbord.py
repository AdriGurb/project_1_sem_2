from io import BytesIO
import base64
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class app_dash():
    def __init__(self, df):
        # Инициализация приложения
        self.app = dash.Dash(__name__)

        # Лейаут приложения
        self.app.layout = html.Div([
            html.H1("Анализ товаров маркетплейсов", style={'textAlign': 'center'}),
            dcc.Tabs([
                dcc.Tab(label='Главная страница', children=[
                    html.Div([
                        html.H3("Анализ товаров маркетплейсов по их оценкам  отзывам"),
                        html.H2("Проведена работа по:"),
                        html.Ul([
                            html.Li("Парсингу товаров с Ozon, Wildberries, Яндекс Маркет с помощью Selenium"),
                            html.Li("Очистка данных от дубликатов и пропусков"),
                            html.Li("Анализу и визуализации графиков"),
                            html.Li("Созданию дэшборда"),
                            html.Li("Формированию отчёта")
                        ])
                    ])
                ]),
                dcc.Tab(label='Данные', children=[
                    html.Div([
                        
                        html.H3("Фильтры"),
                        dcc.Dropdown(
                            id='market-filter',
                            options=[{'label': m, 'value': m} for m in df['market'].unique()],
                            value=df['market'].unique(),
                            multi=True
                        ),
                        dcc.RangeSlider(
                            id='price-range',
                            min=int(df['price'].min()),
                            max=int(df['price'].max()),
                            value=[int(df['price'].min()), int(df['price'].max())]
                        ),
                        
                        html.Div(id='data-metrics'),
                        dcc.Graph(id='market-pie'),
                        
                        
                        html.H3("Описание столбцов:"),
                        html.Ul([
                            html.Li("title - Название из карточки товара"),
                            html.Li("price - Цена товара"),
                            html.Li("rating - Оценка товара по пятибалльной шкале"),
                            html.Li("reviews - Количество отзывов на товар"),
                            html.Li("market - Маркетплейс, на котором выложен товар(ozon, wb, yand)"),
                            html.Li("req - Запрос, по которому искали товар"),
                            html.Li("link  - Ссылка на товар")
                        ])
                    ])
                ]),
                
                dcc.Tab(label='Анализ товаров', children=[
                    html.Div([
                        html.H3("Анализ категории"),
                        dcc.Dropdown(
                            id='category-select',
                            options=[{'label': cat, 'value': cat} for cat in df['req'].unique()],
                            value=df['req'].iloc[0]
                        ),
                        dcc.Graph(id='price-rating-plot'),
                        html.Img(id='correlation-heatmap'),
                        html.Img(id='price-img'),
                        dcc.Graph(id='reviews-dist')
                    ])
                ]),
                dcc.Tab(label='Сравнение маркетплейсов', children=[
                    html.Div([
                        html.H3("Сравнительный анализ маркетплейсов"),
                        
                        # Фильтры
                        html.Div([
                            dcc.Dropdown(
                                id='compare-category-select',
                                options=[{'label': cat, 'value': cat} for cat in df['req'].unique()],
                                value=df['req'].iloc[0],
                                style={'width': '50%', 'margin': '10px'}
                            ),
                            dcc.RangeSlider(
                                id='compare-price-range',
                                min=int(df['price'].min()),
                                max=int(df['price'].max()),
                                value=[int(df['price'].min()), int(df['price'].max())],
                                marks={int(df['price'].min()): str(int(df['price'].min())),
                                       int(df['price'].max()): str(int(df['price'].max()))},
                                step=30
                            )
                        ], style={'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px'}),
                        
                        # Основные метрики
                        html.Div(id='market-comparison-metrics', style={'margin': '20px 0'}),
                        
                        # Графики сравнения
                        html.Div([
                            dcc.Graph(id='price-comparison', style={'width': '49%', 'display': 'inline-block'}),
                            dcc.Graph(id='rating-comparison', style={'width': '49%', 'display': 'inline-block'})
                        ], style={'display': 'flex'}),
                        
                        html.Div([
                            dcc.Graph(id='reviews-comparison', style={'width': '49%', 'display': 'inline-block'}),
                            dcc.Graph(id='products-count', style={'width': '49%', 'display': 'inline-block'})
                        ], style={'display': 'flex', 'marginTop': '20px'}),
                        
                        # Таблица с топ-товарами
                        html.H4("Топ товаров по рейтингу для каждого маркетплейса"),
                        dash_table.DataTable(
                            id='top-products-table',
                            columns=[
                                {"name": "Маркетплейс", "id": "market"},
                                {"name": "Товар", "id": "title"},
                                {"name": "Цена", "id": "price"},
                                {"name": "Рейтинг", "id": "rating"},
                                {"name": "Отзывы", "id": "reviews"}
                            ],
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                                'whiteSpace': 'normal'
                            },
                            page_size=10
                        )
                    ], style={'padding': '20px'})
                ]),
                
                dcc.Tab(label='Выводы', children=[
                    html.Div([
                        html.H3("Ключевые инсайты"),
                        html.Ul([
                            html.Li("Нет значимой корреляции(>0.4) между рейтингом, количеством отзывов и ценой. Возможно из-за того, что товар который стоит дороже оказывается на деле дешевле(6 пар носков за 800 рублей и одна пара за 300)"),
                            html.Li("В категории куртки есть умеренная корреляция (-0,36) между количеством отзывов и рейтингом. Можно предположить, что популярны дешёвые куртки получают больше отзывов, но часто их качество оставляет желать лучшего или у доргих курток более лояльная аудитория"),
                            html.Li("Кружка за 93 рублей казалась странной, но при проверке выяснилось, что она действительно продаётся за 93 рублей."),
                            html.Li("В яндекс маркете значительно меньше отзывов на товары, чем в озоне и на вб. Скорее всего, это из-за того что, он менее популярен и запросы более типичны для вб/озона(на rtx 5090 будет явно больше отзывов в яндекс маркете)"),
                            html.Li("Оценок ниже 3 не было, это связано с тем, что мы брали наиболие полярные и релевантные товары с первой страницы по запросу на маркетплейсе"),
                            html.Li("У носков и курток нормальное расперделение по цене, а у термопасты, кружек и батончиков mars распредиление смещёно вправо"),
                            html.Li("У всех товаров есть бестселлеры, которые по кол-ву отзывов далеко отрываются от остальных конкурентов"),
                            html.Li("В срднем товары на озоне дешевле, чем у конкурентов"),
                            html.Li("В срднем товары на яндекс маркете дороже, чем у конкурентов"),
                            html.Li("В средний рейтинг товаров почти одинаковый у всех маркетплейсов(около 4.8). Только вб в категории куртики немного просел 4.6, когда у остальных по 4.8")
                        ])
                    ])
                ])
            ])
        ])

        # Callbacks для обновления данных
        @self.app.callback(
            [Output('data-metrics', 'children'),
             Output('market-pie', 'figure')],
            [Input('market-filter', 'value'),
             Input('price-range', 'value')], 
        )
        def update_data(markets, price_range):
            filtered_df = df[
                (df['market'].isin(markets)) &
                (df['price'].between(price_range[0], price_range[1]))
            ]
            
            metrics = html.Div([
                html.P(f"Всего товаров: {len(filtered_df)}"),
                html.P(f"Средняя цена: {filtered_df['price'].mean():.2f} ₽"),
                html.P(f"Средний рейтинг: {filtered_df['rating'].mean():.1f}")
            ])
            
            pie_fig = px.pie(
            filtered_df, 
            names='market', 
            title='Распределение по маркетплейсам',
            color='market',
            color_discrete_map={
                    'wb': '#9a63fa',
                    'ozon': '#636EFA',
                    'yand': '#E1CC4F'
                }
        )
            
            return metrics, pie_fig

        def get_img(fig):
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            return 'data:image/png;base64,{}'.format(base64.b64encode(buf.read()).decode('utf-8'))

        def get_correlation_heatmap(category_df, numeric_cols, category):
            if len(numeric_cols) > 1:
                fig, ax = plt.subplots(figsize=(4, 3))
                sns.heatmap(
                    category_df[numeric_cols].corr(), 
                    annot=True, 
                    cmap='coolwarm', 
                    ax=ax,
                    fmt='.2f',  # Формат чисел с двумя знаками после запятой
                    linewidths=.5
                )
                ax.set_title(f'Матрица корреляций для {category}', pad=20)
                plt.tight_layout()
                
                return get_img(fig)
            return None

        def get_hist(category_df, category):
            # Распределение цен
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(category_df['price'], bins=30, kde=True)
            plt.title(f'Распределение цен для {category}')
            plt.xlabel('Цена')
            plt.ylabel('Количество')
            plt.tight_layout()
            
            return get_img(fig)

        # Callbacks для анализа
        @self.app.callback(
            [Output('price-rating-plot', 'figure'),
             Output('reviews-dist', 'figure'),
             Output('correlation-heatmap', 'src'),
             Output('price-img', 'src')],  # Новый Output для heatmap
            [Input('category-select', 'value')]
        )
        def update_analysis(category):
            category_df = df[df['req'] == category]
            
            # 1. Scatter plot Цена vs Рейтинг
            scatter_fig = px.scatter(
                category_df, 
                x='price', 
                y='rating',
                hover_data=['title'],
                color='market', 
                color_discrete_map={
                    'wb': '#9a63fa',
                    'ozon': '#636EFA',
                    'yand': '#E1CC4F'
                },
                title=f'Цена vs Рейтинг для {category}'
            )
            scatter_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))

            
            hist_fig = px.histogram(
                category_df, 
                x='reviews',
                title=f'Распределение отзывов для {category}',
                nbins=20
            )
            hist_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))

            
            numeric_cols = category_df.select_dtypes(include=['number']).columns.tolist()
            heatmap_img = get_correlation_heatmap(category_df, numeric_cols, category)

            price_img = get_hist(category_df, category)
            
            return scatter_fig, hist_fig, heatmap_img, price_img
            
        # Callback для обновления данных сравнения
        @self.app.callback(
            [Output('market-comparison-metrics', 'children'),
             Output('price-comparison', 'figure'),
             Output('rating-comparison', 'figure'),
             Output('reviews-comparison', 'figure'),
             Output('products-count', 'figure'),
             Output('top-products-table', 'data')],
            [Input('compare-category-select', 'value'),
             Input('compare-price-range', 'value')]
        )
        def update_comparison(category, price_range):
            filtered_df = df[(df['req'] == category) & 
                            (df['price'] >= price_range[0]) & 
                            (df['price'] <= price_range[1])]
            
            # 1. Основные метрики
            min_price = filtered_df.groupby('market')['price'].min().round(2)
            avg_price = filtered_df.groupby('market')['price'].mean().round(2)
            avg_rating = filtered_df.groupby('market')['rating'].mean().round(2)
            total_reviews = filtered_df.groupby('market')['reviews'].sum()
            
            metrics = html.Div([
                html.Div([
                    html.H4("Минимальная цена"),
                    html.P(f"WB: {min_price.get('wb', 0)} руб"),
                    html.P(f"Ozon: {min_price.get('ozon', 0)} руб"),
                    html.P(f"Яндекс: {min_price.get('yand', 0)} руб")
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),
                
                html.Div([
                    html.H4("Средняя цена"),
                    html.P(f"WB: {avg_price.get('wb', 0)} руб"),
                    html.P(f"Ozon: {avg_price.get('ozon', 0)} руб"),
                    html.P(f"Яндекс: {avg_price.get('yand', 0)} руб")
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),
                
                html.Div([
                    html.H4("Средний рейтинг"),
                    html.P(f"WB: {avg_rating.get('wb', 0)}"),
                    html.P(f"Ozon: {avg_rating.get('ozon', 0)}"),
                    html.P(f"Яндекс: {avg_rating.get('yand', 0)}")
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),
                
                html.Div([
                    html.H4("Всего отзывов"),
                    html.P(f"WB: {total_reviews.get('wb', 0)}"),
                    html.P(f"Ozon: {total_reviews.get('ozon', 0)}"),
                    html.P(f"Яндекс: {total_reviews.get('yand', 0)}")
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
            
            # 2. График сравнения цен
            price_fig = px.box(
                filtered_df, 
                x='market', 
                y='price',
                color='market',
                color_discrete_map={
                    'wb': '#9a63fa',
                    'ozon': '#636EFA',
                    'yand': '#E1CC4F'
                },
                title='Распределение цен по маркетплейсам'
            )
            
            # 3. График сравнения рейтингов
            rating_fig = px.box(
                filtered_df, 
                x='market', 
                y='rating',
                color='market',
                color_discrete_map={
                    'wb': '#9a63fa',
                    'ozon': '#636EFA',
                    'yand': '#E1CC4F'
                },
                title='Распределение рейтингов по маркетплейсам'
            )
            
            # 4. График сравнения отзывов
            reviews_fig = px.bar(
                filtered_df.groupby('market')['reviews'].sum().reset_index(),
                x='market',
                y='reviews',
                color='market',
                color_discrete_map={
                    'wb': '#9a63fa',
                    'ozon': '#636EFA',
                    'yand': '#E1CC4F'
                },
                title='Общее количество отзывов по маркетплейсам'
            )
            
            # 5. Количество товаров
            count_fig = px.bar(
                filtered_df['market'].value_counts().reset_index(),
                x='market',
                y='count',
                color='market',
                color_discrete_map={
                    'wb': '#9a63fa',
                    'ozon': '#636EFA',
                    'yand': '#E1CC4F'
                },
                title='Количество товаров по маркетплейсам'
            )
            
            # 6. Топ товаров
            top_products = filtered_df.sort_values(['market', 'rating'], ascending=[True, False])
            top_products = top_products.groupby('market').head(3).to_dict('records')
            
            return metrics, price_fig, rating_fig, reviews_fig, count_fig, top_products


        @self.app.callback(
            Output('compare-price-range', 'min'),
            Output('compare-price-range', 'max'),
            Output('compare-price-range', 'value'),
            Output('compare-price-range', 'marks'),
            Input('compare-category-select', 'value')
        )
        def update_price_slider(selected_category):
            # Фильтруем данные по выбранной категории
            category_df = df[df['req'] == selected_category]
            
            if len(category_df) == 0:
                # Если нет данных для категории, возвращаем значения по умолчанию
                return 0, 10000, [0, 10000], {0: '0', 10000: '10000'}
            
            min_price = int(category_df['price'].min())
            max_price = int(category_df['price'].max())
            
            # Создаем метки для слайдера (можно настроить форматирование)
            marks = {
                min_price: str(min_price),
                max_price: str(max_price)
            }
            
            # Возвращаем новые параметры слайдера
            return min_price, max_price, [min_price, max_price], marks
