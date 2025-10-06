# 🔥 Firebase Setup Commands - Run These!

## Step 1: Login to Firebase

**Run this in your terminal:**
```bash
cd "/Users/seanx/code/haunted mansion game /V1"
firebase login
```

This will open a browser for you to authenticate with your Google account.

## Step 2: Initialize Firebase Project

After login, run:
```bash
firebase init
```

**Select these options:**
- ◯ Firestore
- ◯ Functions
- ◯ Hosting
- ◯ Storage (optional, for future features)

**When prompted:**
1. **Use existing project** → Select your GCP project with Gemini API
2. **Firestore rules** → Use default
3. **Firestore indexes** → Use default
4. **Functions language** → Python
5. **Hosting public directory** → `public`
6. **Single-page app** → Yes
7. **Automatic builds with GitHub** → No (for now)

## Step 3: Project Structure

I'll create the necessary files for you:
- Firebase configuration
- Cloud Functions
- Firestore rules
- Frontend with Firebase SDK

## Step 4: Deploy

After I set everything up:
```bash
firebase deploy
```

---

**Please run Step 1 and 2 now, then let me know when done!**

I'll prepare all the files while you're doing that.

