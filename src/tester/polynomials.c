#include <math.h>
#include "polynomials.h"
#include "parameters.h"

#define PARAMETERS 2
#define SECONDS_IN_ONE_HOUR 3600

double linear(double p, double q, double r)
{
    double *theta;
    
    if(PARAMETERS == 1)
    {
        p = p / SECONDS_IN_ONE_HOUR;
        r = r / SECONDS_IN_ONE_HOUR;
        theta = temporal_normalized_lin_parameters; 
    }
    else if(PARAMETERS == 2)
    {
        theta = lublin_256_lin_parameters;
    }
    else if(PARAMETERS == 3)
    {
        theta = ctc_sp2_lin_parameters;
    }
    else if(PARAMETERS == 4)
    {
        theta = sdsc_blue_lin_parameters;
    }
    else
    {
        theta = default_lin_parameters;
    }
    
    return theta[0] \
            + theta[1]*p + theta[2]*q + theta[3]*r;
}

double quadratic(double p, double q, double r)
{
    double *theta;

    if(PARAMETERS == 1)
    {
        p = p / SECONDS_IN_ONE_HOUR;
        r = r / SECONDS_IN_ONE_HOUR;
        theta = temporal_normalized_qdr_parameters; 
    }
    else if(PARAMETERS == 2)
    {
        theta = lublin_256_qdr_parameters;
    }
    else if(PARAMETERS == 3)
    {
        theta = ctc_sp2_qdr_parameters;
    }
    else if(PARAMETERS == 4)
    {
        theta = sdsc_blue_qdr_parameters;
    }
    else
    {
        theta = default_qdr_parameters;
    }
    
    return theta[0] \
            + theta[1]*p + theta[2]*q + theta[3]*r \
            + theta[4]*pow(p,2) + theta[5]*pow(q,2) + theta[6]*pow(r,2) \
            + theta[7]*p*q;
}

double cubic(double p, double q, double r)
{
    double *theta;

    if(PARAMETERS == 1)
    {
        p = p / SECONDS_IN_ONE_HOUR;
        r = r / SECONDS_IN_ONE_HOUR;
        theta = temporal_normalized_cub_parameters; 
    }
    else if(PARAMETERS == 2)
    {
        theta = lublin_256_cub_parameters;
    }
    else if(PARAMETERS == 3)
    {
        theta = ctc_sp2_cub_parameters;
    }
    else if(PARAMETERS == 4)
    {
        theta = sdsc_blue_cub_parameters;
    }
    else
    {
        theta = default_cub_parameters;
    }

    return theta[0] \
            + theta[1]*p + theta[2]*q + theta[3]*r \
            + theta[4]*pow(p,2) + theta[5]*pow(q,2) + theta[6]*pow(r,2) \
            + theta[7]*p*q \
            + theta[8]*pow(p,3) + theta[9]*pow(q,3) + theta[10]*pow(r,3) \
            + theta[11]*pow(p,2)*q + theta[12]*p*pow(q,2);
}

double quartic(double p, double q, double r)
{
    double *theta;

    if(PARAMETERS == 1)
    {
        p = p / SECONDS_IN_ONE_HOUR;
        r = r / SECONDS_IN_ONE_HOUR;
        theta = temporal_normalized_qua_parameters; 
    }
    else if(PARAMETERS == 2)
    {
        theta = lublin_256_qua_parameters;
    }
    else if(PARAMETERS == 3)
    {
        theta = ctc_sp2_qua_parameters;
    }
    else if(PARAMETERS == 4)
    {
        theta = sdsc_blue_qua_parameters;
    }
    else
    {
        theta = default_qua_parameters;
    }

    return theta[0] \
            + theta[1]*p + theta[2]*q + theta[3]*r \
            + theta[4]*pow(p,2) + theta[5]*pow(q,2) + theta[6]*pow(r,2) \
            + theta[7]*p*q \
            + theta[8]*pow(p,3) + theta[9]*pow(q,3) + theta[10]*pow(r,3) \
            + theta[11]*pow(p,2)*q + theta[12]*p*pow(q,2) \
            + theta[13]*pow(p,4) + theta[14]*pow(q,4) + theta[15]*pow(r,4) \
            + theta[16]*pow(p,3)*q + theta[17]*pow(p,2)*pow(q,2) + theta[18]*p*pow(q,3);
}

double quintic(double p, double q, double r)
{
    double *theta;

    if(PARAMETERS == 1)
    {
        p = p / SECONDS_IN_ONE_HOUR;
        r = r / SECONDS_IN_ONE_HOUR;
        theta = temporal_normalized_qui_parameters; 
    }
    else if(PARAMETERS == 2)
    {
        theta = lublin_256_qui_parameters;
    }
    else if(PARAMETERS == 3)
    {
        theta = ctc_sp2_qui_parameters;
    }
    else if(PARAMETERS == 4)
    {
        theta = sdsc_blue_qui_parameters;
    }
    else
    {
        theta = default_qui_parameters;
    }

    return theta[0] \
            + theta[1]*p + theta[2]*q + theta[3]*r \
            + theta[4]*pow(p,2) + theta[5]*pow(q,2) + theta[6]*pow(r,2) \
            + theta[7]*p*q \
            + theta[8]*pow(p,3) + theta[9]*pow(q,3) + theta[10]*pow(r,3) \
            + theta[11]*pow(p,2)*q + theta[12]*p*pow(q,2) \
            + theta[13]*pow(p,4) + theta[14]*pow(q,4) + theta[15]*pow(r,4) \
            + theta[16]*pow(p,3)*q + theta[17]*pow(p,2)*pow(q,2) + theta[18]*p*pow(q,3) \
            + theta[19]*pow(p,5) + theta[20]*pow(q,5) + theta[21]*pow(r,5) \
            + theta[22]*pow(p,4)*q + theta[23]*pow(p,3)*pow(q,2) \
            + theta[24]*pow(p,2)*pow(q,3) + theta[25]*p*pow(q,4);
}

double sextic(double p, double q, double r)
{
    double *theta;
    
    if(PARAMETERS == 1)
    {
        p = p / SECONDS_IN_ONE_HOUR;
        r = r / SECONDS_IN_ONE_HOUR;
        theta = temporal_normalized_sex_parameters; 
    }
    else if(PARAMETERS == 2)
    {
        theta = lublin_256_sex_parameters;
    }
    else if(PARAMETERS == 3)
    {
        theta = ctc_sp2_sex_parameters;
    }
    else if(PARAMETERS == 4)
    {
        theta = sdsc_blue_sex_parameters;
    }
    else
    {
        theta = default_sex_parameters;
    }

    return theta[0] \
            + theta[1]*p + theta[2]*q + theta[3]*r \
            + theta[4]*pow(p,2) + theta[5]*pow(q,2) + theta[6]*pow(r,2) \
            + theta[7]*p*q \
            + theta[8]*pow(p,3) + theta[9]*pow(q,3) + theta[10]*pow(r,3) \
            + theta[11]*pow(p,2)*q + theta[12]*p*pow(q,2) \
            + theta[13]*pow(p,4) + theta[14]*pow(q,4) + theta[15]*pow(r,4) \
            + theta[16]*pow(p,3)*q + theta[17]*pow(p,2)*pow(q,2) + theta[18]*p*pow(q,3) \
            + theta[19]*pow(p,5) + theta[20]*pow(q,5) + theta[21]*pow(r,5) \
            + theta[22]*pow(p,4)*q + theta[23]*pow(p,3)*pow(q,2) \
            + theta[24]*pow(p,2)*pow(q,3) + theta[25]*p*pow(q,4) \
            + theta[26]*pow(p,6) + theta[27]*pow(q,6) + theta[28]*pow(r,6) \
            + theta[29]*pow(p,5)*q + theta[30]*pow(p,4)*pow(q,2) \
            + theta[31]*pow(p,3)*pow(q,3) \
            + theta[32]*pow(p,2)*pow(q,4) + theta[33]*p*pow(q,5);
}