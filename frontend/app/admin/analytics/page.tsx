"use client";

import React, { useEffect, useState } from 'react';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  BookOpen, 
  Activity, 
  Award,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getDashboardData } from '@/lib/admin-analytics-service';

interface DashboardData {
  overview: {
    total_users: number;
    total_learners: number;
    total_instructors: number;
    total_courses: number;
    total_enrollments: number;
    total_revenue: number;
    active_subscriptions: number;
    avg_courses_per_instructor: number;
  };
  user_growth: {
    new_users: number;
    growth_rate_percentage: number;
    daily_signups: { date: string; count: number }[];
  };
  engagement: {
    dau: number;
    wau: number;
    mau: number;
    dau_mau_ratio: number;
    avg_study_time_minutes: number;
    course_completion_rate: number;
  };
  revenue: {
    period_revenue: number;
    mrr: number;
    avg_transaction_value: number;
    daily_revenue: { date: string; revenue: number; transactions: number }[];
  };
  top_courses: {
    course_id: string;
    title: string;
    enrollments: number;
    rating: number;
  }[];
  top_instructors: {
    instructor_id: string;
    name: string;
    course_count: number;
    total_enrollments: number;
    total_earnings: number;
  }[];
  system_health: {
    active_sessions: number;
    status: string;
    uptime_percentage: number;
  };
}

export default function AdminDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    fetchDashboardData();
  }, [selectedPeriod]);

  const fetchDashboardData = async () => {
    try {
      const dashboardData = await getDashboardData();
      setData(dashboardData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-12 bg-gray-300 rounded w-1/3 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-300 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div>Error loading dashboard</div>;
  }

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon: Icon, 
    color 
  }: { 
    title: string; 
    value: string | number; 
    change?: string; 
    icon: any; 
    color: string;
  }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="text-white" size={24} />
        </div>
        {change && (
          <span className={`text-sm font-semibold ${
            change.startsWith('+') ? 'text-green-600' : 'text-red-600'
          }`}>
            {change}
          </span>
        )}
      </div>
      <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Admin Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Platform performance and metrics</p>
          </div>

          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-4 py-2"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={data.overview.total_users.toLocaleString()}
            change={`+${data.user_growth.growth_rate_percentage}%`}
            icon={Users}
            color="bg-blue-500"
          />
          <StatCard
            title="Total Revenue"
            value={`$${data.overview.total_revenue.toLocaleString()}`}
            change={`MRR: $${data.revenue.mrr.toLocaleString()}`}
            icon={DollarSign}
            color="bg-green-500"
          />
          <StatCard
            title="Total Courses"
            value={data.overview.total_courses.toLocaleString()}
            icon={BookOpen}
            color="bg-purple-500"
          />
          <StatCard
            title="Total Enrollments"
            value={data.overview.total_enrollments.toLocaleString()}
            icon={Award}
            color="bg-orange-500"
          />
        </div>

        {/* Engagement Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Daily Active Users (DAU)"
            value={data.engagement.dau.toLocaleString()}
            icon={Activity}
            color="bg-indigo-500"
          />
          <StatCard
            title="Monthly Active Users (MAU)"
            value={data.engagement.mau.toLocaleString()}
            change={`DAU/MAU: ${data.engagement.dau_mau_ratio}%`}
            icon={Users}
            color="bg-pink-500"
          />
          <StatCard
            title="Completion Rate"
            value={`${data.engagement.course_completion_rate.toFixed(1)}%`}
            icon={TrendingUp}
            color="bg-cyan-500"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* User Growth Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BarChartIcon size={20} className="text-blue-500" />
              User Growth
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.user_growth.daily_signups}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3B82F6" name="New Users" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Revenue Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <PieChartIcon size={20} className="text-green-500" />
              Daily Revenue
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.revenue.daily_revenue}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#10B981" strokeWidth={2} name="Revenue ($)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Courses & Instructors */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Top Courses */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Top Courses</h3>
            <div className="space-y-3">
              {data.top_courses.map((course, index) => (
                <div key={course.course_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                    <div>
                      <p className="font-semibold text-gray-800">{course.title}</p>
                      <p className="text-sm text-gray-600">{course.enrollments} enrollments</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-yellow-500">★</span>
                    <span className="font-semibold">{course.rating.toFixed(1)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Instructors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Top Instructors</h3>
            <div className="space-y-3">
              {data.top_instructors.map((instructor, index) => (
                <div key={instructor.instructor_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                    <div>
                      <p className="font-semibold text-gray-800">{instructor.name}</p>
                      <p className="text-sm text-gray-600">
                        {instructor.course_count} courses • {instructor.total_enrollments} students
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">
                      ${instructor.total_earnings.toFixed(0)}
                    </p>
                    <p className="text-xs text-gray-500">earnings</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-gray-600 text-sm mb-1">Status</p>
              <p className="text-xl font-bold text-green-600 capitalize">{data.system_health.status}</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-gray-600 text-sm mb-1">Active Sessions</p>
              <p className="text-xl font-bold text-blue-600">{data.system_health.active_sessions}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-gray-600 text-sm mb-1">Uptime</p>
              <p className="text-xl font-bold text-purple-600">{data.system_health.uptime_percentage}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
