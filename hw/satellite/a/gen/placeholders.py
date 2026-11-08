"""Write an empty sheet for every block that has no generated file yet, so the project opens and ERC runs."""
import hier
for name, *_ in hier.SHEETS:
    s = hier.SubSheet(name)
    if not s.file.exists():
        s.text("Placeholder: this block's generator has not run yet.", (25.4, 25.4))
        s.save()
        print("placeholder", s.file.name)
