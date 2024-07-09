from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import json
import re

app = Flask(__name__)


def load_and_segment_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    paragraphs = [para.strip() for para in text.split('\n\n') if para.strip()]
    return paragraphs


def split_paragraph(paragraph_text):
    pattern = r'(?<!\w\.\w)(?<![A-Z][a.z]\.)(?<=\.|\,|\;|\?)\s'
    slices = re.split(pattern, paragraph_text)
    return slices


@app.route('/', methods=['GET', 'POST'])
def index():
    verses_df = pd.read_csv('data/verses_1.csv')
    paragraphs = load_and_segment_text('data/ganguly_1.txt')
    translation_df = pd.read_csv('data/translation_master_1.csv')

    try:
        with open('temp/unselected_options.json', 'r') as file:
            unselected_options = json.load(file)
    except FileNotFoundError:
        unselected_options = {}

    current_index = int(request.args.get('index', 0)) if 'index' in request.args else 0

    if request.method == 'POST':
        selected_translations = request.form.getlist('selected_translation')
        selected_translation = " ".join(selected_translations).strip()

        if 'save' in request.form:
            translation_df.at[current_index, 'Translation'] = selected_translation
            translation_df.to_csv('data/translation_master_1.csv', index=False)

        next_index = current_index + 1 if 'next' in request.form or 'save' in request.form else current_index

        current_options = split_paragraph(paragraphs[current_index] if current_index < len(paragraphs) else "")
        current_paragraph = paragraphs[current_index] if current_index < len(paragraphs) else ""
        unselected = [opt for opt in current_options if
                      opt not in selected_translations and opt.strip() and opt != current_paragraph]

        unselected_options[str(next_index)] = unselected
        with open('temp/unselected_options.json', 'w') as file:
            json.dump(unselected_options, file)

        return redirect(url_for('index', index=next_index))

    current_paragraph = paragraphs[current_index] if current_index < len(paragraphs) else ""
    current_options = split_paragraph(current_paragraph)

    if current_index > 0:
        previous_translation = translation_df.loc[current_index - 1, 'Translation'].split() if current_index > 0 else []
        filtered_previous = [opt for opt in unselected_options.get(str(current_index), []) if
                             opt not in previous_translation]
    else:
        filtered_previous = unselected_options.get(str(current_index), [])

    remaining_options = [opt for opt in current_options if opt not in filtered_previous and opt != current_paragraph]

    return render_template('index.html', current_index=current_index, total_verses=len(verses_df),
                           verse=verses_df.iloc[current_index], unselected_from_previous=filtered_previous,
                           remaining_options=remaining_options, selected=current_paragraph,
                           master_translation=translation_df.to_html())


if __name__ == '__main__':
    app.run(debug=True)
