# Adding or Improving a KillerPDF Translation

## File format

Each language is a single JSON file in the `LOCALES/` folder. The JSON file must be in the directory and the language must be present in the i18n.py file:

- `en.json` - English
- `es.json` - Spanish
- `ru.json` - Russian

## How to contribute

### Editing an existing translation

1. Open the file for your language in GitHub (e.g. `LOCALES/es.json`)
2. Click the pencil icon to edit
3. Translate the text on the right-hand side of the key (in quotes; "")
4. Click "Commit changes" and open a pull request

### Adding a new language

1. Copy `LOCALES/en.json` and add it to the i18n.py file under the "Supported Languages" section.
2. Translate the values. If you are to do all of them, you can save your work: any key you do not translate will automatically fall back to the English text, and if that is not available it will show the key name itself.
3. Open a pull request with the new file.

## Format string example

```json
  "common.add": "Add",
  "common.edit": "Edit",
  "common.delete": "Delete",
  "common.save": "Save",
```

## Testing your translation

You can load your translation files into the LOCALES\ directory. Ensure your language is also present in the i18n.py file then run the program as normal.

To change the language use the "Language Settings" selection in the toolbar under "Options". The program will reload once you select the language but upon its relaunch, it should be in the new language.

## Questions

Open a GitHub issue or leave a comment on your pull request.