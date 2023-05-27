import sass

scss_file = "./static/scss/styles.scss"
css_file = "./static/css/styles.css"

# Compilar el archivo SCSS a CSS
sass.compile(
    filename=scss_file,
    output_style='compressed',
    include_paths=['./static/scss/'],
    output=css_file
)