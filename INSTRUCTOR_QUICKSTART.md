# Quick Start Guide - Instructor Platform

## Prerequisites
- Backend server running on `http://localhost:8000`
- Frontend server running on `http://localhost:3000`
- Database migrations applied

## Step-by-Step Testing Guide

### 1. Register as an Instructor (2 minutes)

1. Navigate to `http://localhost:3000/register`
2. Click on the **"Teach"** button (right side)
3. Fill in the form:
   - Full Name: `John Instructor`
   - Email: `john.instructor@example.com`
   - Password: `instructor123` (min 8 chars with letter & digit)
   - Confirm Password: `instructor123`
4. Click **"Create Account"**
5. You should be automatically redirected to `/instructor/dashboard`

### 2. Explore the Dashboard (1 minute)

You'll see:
- **Stats cards** showing: Total Courses (0), Total Students (0), Avg Rating (0.0), Revenue ($0)
- **Quick Actions** with links to create courses, manage courses, and view students
- **Course Performance** section (empty for now)

### 3. Create Your First Course (3 minutes)

1. Click **"Create Course"** button (top right or in Quick Actions)
2. Fill in the course details:
   
   **Basic Information:**
   - Course Title: `Introduction to Python Programming`
   - Short Description: `Learn Python from scratch in this beginner-friendly course`
   - Full Description: `This comprehensive course covers Python fundamentals including variables, data types, control structures, functions, and object-oriented programming. Perfect for beginners with no prior coding experience.`
   - Difficulty Level: `Beginner`
   - Estimated Duration: `40` hours
   - Thumbnail URL: `https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800` (optional)
   
   **Skills Taught:**
   - Type `Python` and click Add
   - Type `Programming Basics` and click Add
   - Type `Problem Solving` and click Add
   
   **Prerequisites:**
   - Type `Basic computer knowledge` and click Add
   - Type `Willingness to learn` and click Add

3. Click **"Create Course"**
4. You'll be redirected to the course editor

### 4. Add Modules to Your Course (2 minutes)

1. In the course editor, click **"+ Module"** button on the right sidebar
2. Fill in module details:
   - Module Title: `Getting Started with Python`
   - Description: `Introduction to Python and setting up your environment`
   - Sequence Order: `1` (automatically filled)
   - Duration: `120` minutes
3. Click **"Create Module"**
4. The module appears in the sidebar

Repeat to add more modules:
- Module 2: `Variables and Data Types`
- Module 3: `Control Flow and Loops`
- Module 4: `Functions and Modules`

### 5. Publish Your Course (30 seconds)

1. Click the **"Publish"** button (top right)
2. The status changes to "Published"
3. The course is now visible to learners

### 6. View Your Courses (1 minute)

1. Navigate to **"My Courses"** from the sidebar
2. You'll see your course listed with:
   - Course thumbnail
   - Title and description
   - Status badge (Published)
   - Enrollment count (0)
   - Edit, Publish/Unpublish, and Delete buttons

3. Try the **search** and **filter** features:
   - Search: Type "Python"
   - Filter: Click "Published", "Draft", or "All"

### 7. Check Analytics (1 minute)

1. Go back to **"Dashboard"** from the sidebar
2. You should now see:
   - Total Courses: `1`
   - Other stats still at `0` (no students yet)
3. The **Course Performance** table shows your course with:
   - 0 enrollments
   - 0 active students
   - 0% completion rate
   - Rating N/A

### 8. View Students Page (30 seconds)

1. Navigate to **"Students"** from the sidebar
2. You'll see empty state: "No students yet"
3. Stats show all zeros (no enrollments)

### 9. Test Course Editing (2 minutes)

1. Go to **"My Courses"**
2. Click **"Edit"** on your Python course
3. Try updating:
   - Change the description
   - Add more skills
   - Modify duration
4. Click **"Save Changes"**
5. Success message appears

### 10. Create Another Course (Optional)

Create a second course to see how the dashboard handles multiple courses:
- Title: `Advanced JavaScript Patterns`
- Difficulty: `Advanced`
- Add different skills and prerequisites

## Testing with Students (Simulated)

To see the full instructor experience with students:

1. **Option A: Create test enrollments via backend**
   - Use the backend admin or API to create test enrollments
   - Students will appear in the Students page
   - Analytics will populate

2. **Option B: Register as a learner**
   - Open incognito/private window
   - Register as a learner (select "Learn")
   - Enroll in the instructor's courses
   - Complete some progress
   - Switch back to instructor account to see analytics

## API Testing (For Developers)

Test the new instructor APIs using the interactive docs:

1. Navigate to `http://localhost:8000/docs`
2. Find the **"Instructor"** section
3. Try these endpoints:

```bash
GET /api/v1/instructor/stats
GET /api/v1/instructor/courses/stats
GET /api/v1/instructor/students
GET /api/v1/instructor/courses/{course_id}/analytics
```

## Features to Explore

### ✅ Completed Features
- [x] Instructor registration with role selection
- [x] Role-based login redirect
- [x] Instructor dashboard with analytics
- [x] Course creation and editing
- [x] Module management
- [x] Course publishing/unpublishing
- [x] Student list and monitoring
- [x] Course performance analytics
- [x] Search and filter functionality
- [x] Responsive design

### 🚧 Future Enhancements
- [ ] Lesson editor with rich text
- [ ] Video content upload
- [ ] Quiz creation
- [ ] Assignment grading
- [ ] Live chat with students
- [ ] Revenue tracking
- [ ] Certificate generation
- [ ] Bulk operations
- [ ] Export reports

## Troubleshooting

### Can't see instructor dashboard after registration?
- Check if you selected "Teach" during registration
- Verify the user role in the database
- Clear browser cache and try logging in again

### Courses not appearing?
- Make sure you're logged in as the correct instructor
- Check if the course was created successfully
- Verify database connection

### Stats showing zero?
- This is normal for a fresh account
- Create courses and wait for student enrollments
- Test with sample data if needed

### API errors?
- Check backend server is running
- Verify authentication token is valid
- Check browser console for detailed errors

## Next Steps

1. **Add lesson content** (when lesson editor is built)
2. **Set up payments** (for paid courses)
3. **Enable discussions** (course forums)
4. **Create quizzes** (assessments)
5. **Launch your first course!**

## Support

For issues or questions:
- Check the main documentation: `INSTRUCTOR_PLATFORM_GUIDE.md`
- Review API docs: `http://localhost:8000/docs`
- Check backend logs for errors
- Review frontend console for debugging

---

**Congratulations!** 🎉 You now have a fully functional instructor platform. Happy teaching!
