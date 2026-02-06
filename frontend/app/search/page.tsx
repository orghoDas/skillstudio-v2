'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { searchCourses, getPopularCategories, type SearchFilters, type CategoryCount } from '@/lib/search-service';
import CoursePriceDisplay from '@/components/CoursePriceDisplay';

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [courses, setCourses] = useState<any[]>([]);
  const [categories, setCategories] = useState<CategoryCount[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState('');
  
  const [filters, setFilters] = useState<SearchFilters>({
    query: searchParams.get('q') || '',
    category: searchParams.get('category') || '',
    level: (searchParams.get('level') as any) || '',
    is_free: searchParams.get('is_free') === 'true' ? true : searchParams.get('is_free') === 'false' ? false : undefined,
    is_certified: searchParams.get('is_certified') === 'true' ? true : undefined,
    min_rating: searchParams.get('min_rating') ? parseFloat(searchParams.get('min_rating')!) : undefined,
    sort_by: (searchParams.get('sort_by') as any) || 'relevance',
    limit: 12,
    offset: 0,
  });

  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    performSearch();
  }, [filters]);

  async function loadCategories() {
    try {
      const data = await getPopularCategories(20);
      setCategories(data.categories);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  }

  async function performSearch() {
    try {
      setLoading(true);
      setError('');
      const data = await searchCourses(filters);
      setCourses(data.courses || []);
      setTotal(data.total);
      setHasMore(data.has_more);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function updateFilter(key: string, value: any) {
    const newFilters = { ...filters, [key]: value, offset: 0 };
    setFilters(newFilters);
    
    // Update URL
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        params.set(k, v.toString());
      }
    });
    router.push(`/search?${params.toString()}`);
  }

  function clearFilters() {
    const newFilters: SearchFilters = {
      query: filters.query,
      sort_by: 'relevance',
      limit: 12,
      offset: 0,
    };
    setFilters(newFilters);
    router.push(`/search?q=${filters.query || ''}`);
  }

  function loadMore() {
    setFilters({ ...filters, offset: filters.offset! + filters.limit! });
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Search Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <input
              type="text"
              value={filters.query || ''}
              onChange={(e) => updateFilter('query', e.target.value)}
              placeholder="Search courses..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>Filters</span>
            </button>
          </div>

          {/* Results count */}
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {loading ? 'Searching...' : `${total} course${total !== 1 ? 's' : ''} found`}
            </p>
            
            <select
              value={filters.sort_by}
              onChange={(e) => updateFilter('sort_by', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm"
            >
              <option value="relevance">Most Relevant</option>
              <option value="popular">Most Popular</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Newest</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <aside className={`lg:w-64 ${showFilters ? 'block' : 'hidden lg:block'}`}>
            <div className="bg-white rounded-lg shadow p-6 sticky top-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
                <button
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-6">
                {/* Category Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={filters.category || ''}
                    onChange={(e) => updateFilter('category', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">All Categories</option>
                    {categories.map((cat) => (
                      <option key={cat.name} value={cat.name}>
                        {cat.name} ({cat.course_count})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Level Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Level
                  </label>
                  <select
                    value={filters.level || ''}
                    onChange={(e) => updateFilter('level', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">All Levels</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                {/* Price Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="price"
                        checked={filters.is_free === undefined}
                        onChange={() => updateFilter('is_free', undefined)}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span className="ml-2 text-sm text-gray-700">All Courses</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="price"
                        checked={filters.is_free === true}
                        onChange={() => updateFilter('is_free', true)}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span className="ml-2 text-sm text-gray-700">Free Only</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="price"
                        checked={filters.is_free === false}
                        onChange={() => updateFilter('is_free', false)}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span className="ml-2 text-sm text-gray-700">Paid Only</span>
                    </label>
                  </div>
                </div>

                {/* Rating Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Rating
                  </label>
                  <select
                    value={filters.min_rating || ''}
                    onChange={(e) => updateFilter('min_rating', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">Any Rating</option>
                    <option value="4.5">4.5 ⭐ & up</option>
                    <option value="4.0">4.0 ⭐ & up</option>
                    <option value="3.5">3.5 ⭐ & up</option>
                    <option value="3.0">3.0 ⭐ & up</option>
                  </select>
                </div>

                {/* Certified Filter */}
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.is_certified || false}
                      onChange={(e) => updateFilter('is_certified', e.target.checked || undefined)}
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Certified Courses Only</span>
                  </label>
                </div>
              </div>
            </div>
          </aside>

          {/* Results */}
          <main className="flex-1">
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {loading && courses.length === 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow animate-pulse">
                    <div className="h-48 bg-gray-200 rounded-t-lg"></div>
                    <div className="p-4 space-y-3">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : courses.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">No courses found</h3>
                <p className="mt-2 text-sm text-gray-500">Try adjusting your search or filters</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {courses.map((course) => (
                    <Link
                      key={course.id}
                      href={`/dashboard/courses/${course.id}`}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow group"
                    >
                      {course.thumbnail_url && (
                        <img
                          src={course.thumbnail_url}
                          alt={course.title}
                          className="w-full h-48 object-cover rounded-t-lg"
                        />
                      )}
                      <div className="p-4">
                        <h3 className="font-semibold text-lg text-gray-900 group-hover:text-blue-600 mb-2">
                          {course.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {course.description}
                        </p>
                        
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center text-sm text-gray-600">
                            <span className="capitalize">{course.level}</span>
                            {course.category && (
                              <>
                                <span className="mx-2">•</span>
                                <span>{course.category}</span>
                              </>
                            )}
                          </div>
                        </div>

                        {course.average_rating > 0 && (
                          <div className="flex items-center mb-3">
                            <span className="text-yellow-500 text-sm">⭐</span>
                            <span className="ml-1 text-sm font-medium text-gray-900">
                              {course.average_rating.toFixed(1)}
                            </span>
                            <span className="ml-1 text-sm text-gray-500">
                              ({course.enrollment_count} students)
                            </span>
                          </div>
                        )}

                        <CoursePriceDisplay courseId={course.id} showButton={false} />
                      </div>
                    </Link>
                  ))}
                </div>

                {/* Load More */}
                {hasMore && (
                  <div className="mt-8 text-center">
                    <button
                      onClick={loadMore}
                      disabled={loading}
                      className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                    >
                      {loading ? 'Loading...' : 'Load More'}
                    </button>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
