

if __name__ == '__main__':
    from tkinter import filedialog
    from tkinter import *
    import pandas as pd

    df = pd.DataFrame({'A': [1,2,3]})
    print(df)

    root = Tk()
    root.filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                 filetypes=(("jpeg files", "*.xlsx"), ("all files", "*.*")))
    print(root.filename)
