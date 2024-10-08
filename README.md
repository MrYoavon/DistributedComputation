## איך להריץ את התוכנית ומה התוצאה

### שלבי הרצת התוכנית:

1. **הפעלת השרת:**
   - תחילה יש להפעיל את השרת באמצעות הפקודה:
     ```bash
     python server.py
     ```
   - השרת יאזין לחיבורים חדשים מלקוחות (Clients) ויתחיל לחלק להם את העבודה – כל לקוח יקבל טווח מספרים לבדוק אותו מול ערך ה-MD5 המבוקש.
   
2. **הפעלת הלקוח:**
   - על מנת להתחבר לשרת ולהתחיל בחיפוש המספר המתאים, יש להריץ את הלקוח בעזרת הפקודה:
     ```bash
     python client.py --ip [של השרת IP כתובת] --port [פורט השרת]
     ```
   - הלקוח ישלח תחילה לשרת מידע על מספר הליבות (cores) הזמינות במחשב בו הוא רץ. לאחר מכן, השרת יחלק את העבודה בין הלקוחות המחוברים.

3. **תהליך החיפוש:**
   - השרת שולח לכל לקוח טווח מספרים (לפי גודל שנקבע מראש) שעליו לבדוק. הלקוח מחשב עבור כל מספר בטווח את ערך ה-MD5 שלו ומשווה אותו לערך ה-MD5 שהתקבל מהשרת.
   - הלקוח מחלק את הטווח שקיבל מהשרת בין מספר ליבות המחשב, כך שכל ליבה בודקת חלק מהטווח. במידה ואחד מהלקוחות מוצא את המספר המתאים, הוא מודיע לשרת ומפסיק את החיפוש.

4. **תוצאה סופית:**
   - כאשר אחד הלקוחות מוצא את המספר התואם, השרת שולח הודעת "stop" לכל הלקוחות הנותרים, כדי לעצור את החיפוש.
   - לאחר סיום התהליך, כל לקוח שסיים את תפקידו מנתק את החיבור לשרת, והשרת סוגר את החיבור בצורה מסודרת.

### תוצאה:
- התוכנית רצה בצורה מבוזרת על גבי מספר מחשבים (לקוחות), כאשר כל לקוח משתמש בכל הליבות הזמינות במחשב שלו לבדיקת טווח המספרים שקיבל מהשרת.
- התוצאה היא חלוקת עומס בין מספר מכשירים, דבר המוביל לחיפוש מהיר ויעיל יותר של המספר התואם ל-MD5 המבוקש.
