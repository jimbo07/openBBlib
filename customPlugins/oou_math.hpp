#ifndef OOU_MATH_H
#define OOU_MATH_H

inline float clamp(float x, float a, float b) { return x < a ? a : (x > b ? b : x); }
inline float linear(float x, float a, float b)
{
	x = clamp((x - a)/(b - a), a, b);
	return x;
}
inline float smooth(float x, float a, float b)
{
	x = clamp((x - a)/(b - a), a, b);
	return x*x*x*(x * (x * 6 - 15) + 10);
}
inline float squared(float x, float a, float b)
{
	x = clamp((x - a)/(b - a), a, b);
	return x*x;
}
inline float invsquared(float x, float a, float b)
{
	x = 1- clamp((x - a)/(b - a), a, b);
	return 1 - x*x;
}
inline float cubed(float x, float a, float b)
{
	x = clamp((x - a)/(b - a), a, b);
	return x*x*x;
}
inline float invcubed(float x, float a, float b)
{
	x = 1- clamp((x - a)/(b - a), a, b);
	return 1 - x*x*x;
}

#endif // OOU_MATH_H
