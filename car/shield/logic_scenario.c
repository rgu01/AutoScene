// Run as
//    test: 
//    echo "\n\n" && gcc -Wall shield.c -o shield.o && ./shield.o
//    library:
//    gcc -c -fPIC shield.c -o shield.o && gcc -shared -o libshield.so shield.o

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <float.h>

typedef int int32_t;
typedef char bool;
typedef int id_t;
typedef int uint16_t;
typedef int uint8_t;

#define true 1
#define false 0
#define None -1
/**capture define start*/
// Constants used for lane network configuration
#define MAXP 40          // Maximum number of points in a boundary
#define MAXPRE 1         // Maximum number of predecessor lanes
#define MAXSUC 1         // Maximum number of successor lanes
#define MAXL 3           // Maximum number of lanes in the lane network
#define INIT_LANE_EGO 30626   // Initial lane ID for the ego vehicle
#define INIT_LANE_TEST 30624  // Initial lane ID for the testing vehicle
/**capture define end*/

// Structure representing a 2D point with double precision
typedef struct {
    double x;
    double y;
} ST_DPOINT;

// Structure representing a line segment defined by two endpoints
typedef struct {
    ST_DPOINT ends[2];  // Array of two points representing the start and end of the line
} ST_DLINE;

// Structure representing a lane boundary, which may be dashed or solid
typedef struct {
    ST_DPOINT points[MAXP];  // Array of points defining the boundary shape
    bool dashLine;           // Flag indicating if the boundary is dashed
} ST_BOUND;

// Structure representing a lane in the lane network
typedef struct {
    id_t ID;                     // Unique identifier for the lane
    ST_BOUND left;               // Left boundary of the lane
    ST_BOUND center;
    ST_BOUND right;              // Right boundary of the lane
    id_t predecessor[MAXPRE];    // Array of predecessor lane IDs
    id_t successor[MAXSUC];      // Array of successor lane IDs
    id_t adjLeft;                // ID of adjacent lane to the left
    bool dirLeft;                // Is the direction of the left adjacency the same
    id_t adjRight;               // ID of adjacent lane to the right
    bool dirRight;               // Is the direction of the right adjacency the same
    double length;               // Length of the lane
} ST_LANE;

/**capture lanelet start */
ST_LANE laneNet[MAXL] = {
{30622, {{
        {-39.289100, -2.153000}, {-20.817100, -1.962500}, {-20.704300, -1.961400}, {-0.034304, -1.748300},
        {0.078531, -1.747100}, {21.383300, -1.527500}, {21.496100, -1.526300}, {26.728000, -1.472400},
        {26.744600, -1.472200}, {32.025300, -1.417700}, {32.183100, -1.416100}, {37.340300, -1.362900},
        {37.548300, -1.360800}, {42.917900, -1.305400}, {43.030700, -1.304200}, {71.898000, -1.006500},
        {72.010800, -1.005400}, {95.114400, -0.767040}, {95.227200, -0.765870}, {120.091800, -0.509360},
        {120.204600, -0.508190}, {154.676800, -0.152500}, {154.789600, -0.151330}, {182.083000, 0.130340},
        {182.195800, 0.131510}, {207.366500, 0.391320}, {207.479300, 0.392480}, {228.168300, 0.606060},
        {228.281100, 0.607220}, {256.799900, 0.901680}, {256.912700, 0.902840}, {286.195600, 1.205200},
        {286.308400, 1.206400}, {310.573300, 1.457000}, {310.686100, 1.458200}, {334.148100, 1.700500},
        {334.260900, 1.701700}, {363.910300, 2.008000}, {364.023100, 2.009200}, {387.272600, 2.249400}
    }, false}, {{
        {-39.213450, -4.016800}, {-20.797900, -3.826950}, {-20.685100, -3.825800}, {-0.015082, -3.612700},
        {0.097755, -3.611550}, {21.402500, -3.391900}, {21.515350, -3.390700}, {26.747250, -3.336800},
        {26.763850, -3.336600}, {32.044550, -3.282100}, {32.202300, -3.280500}, {37.359500, -3.227300},
        {37.567550, -3.225200}, {42.937100, -3.169800}, {43.049950, -3.168600}, {71.917250, -2.870900},
        {72.030050, -2.869750}, {95.133650, -2.631420}, {95.246450, -2.630235}, {120.111050, -2.373730},
        {120.223850, -2.372545}, {154.696050, -2.016850}, {154.808850, -2.015715}, {182.102250, -1.734030},
        {182.215050, -1.732845}, {207.385750, -1.473040}, {207.498550, -1.471860}, {228.187550, -1.258270},
        {228.300350, -1.257140}, {256.819150, -0.962660}, {256.931950, -0.961480}, {286.214850, -0.659100},
        {286.327650, -0.657950}, {310.592550, -0.407300}, {310.705350, -0.406150}, {334.167350, -0.163800},
        {334.280200, -0.162600}, {363.929550, 0.143700}, {364.042350, 0.144900}, {387.348300, 0.385700}
    }, false}, {{
        {-39.137800, -5.880600}, {-20.778700, -5.691400}, {-20.665900, -5.690200}, {0.004140, -5.477100},
        {0.116980, -5.476000}, {21.421700, -5.256300}, {21.534600, -5.255100}, {26.766500, -5.201200},
        {26.783100, -5.201000}, {32.063800, -5.146500}, {32.221500, -5.144900}, {37.378700, -5.091700},
        {37.586800, -5.089600}, {42.956300, -5.034200}, {43.069200, -5.033000}, {71.936500, -4.735300},
        {72.049300, -4.734100}, {95.152900, -4.495800}, {95.265700, -4.494600}, {120.130300, -4.238100},
        {120.243100, -4.236900}, {154.715300, -3.881200}, {154.828100, -3.880100}, {182.121500, -3.598400},
        {182.234300, -3.597200}, {207.405000, -3.337400}, {207.517800, -3.336200}, {228.206800, -3.122600},
        {228.319600, -3.121500}, {256.838400, -2.827000}, {256.951200, -2.825800}, {286.234100, -2.523400},
        {286.346900, -2.522300}, {310.611800, -2.271600}, {310.724600, -2.270500}, {334.186600, -2.028100},
        {334.299500, -2.026900}, {363.948800, -1.720600}, {364.061600, -1.719400}, {387.424000, -1.478000}
    }, false}, None, None, 30624, true, None, false, 426.584468},
{30624, {{
        {-39.272800, 1.343100}, {-20.853200, 1.533000}, {-20.800900, 1.533500}, {-0.070338, 1.747200},
        {-0.018020, 1.747800}, {21.347200, 1.968000}, {21.399600, 1.968600}, {26.708600, 2.023300},
        {26.835800, 2.024600}, {31.989300, 2.077800}, {32.226700, 2.080200}, {37.304200, 2.132600},
        {37.354400, 2.133100}, {42.881800, 2.190100}, {42.934200, 2.190600}, {71.862000, 2.488900},
        {71.914300, 2.489500}, {95.078300, 2.728400}, {95.130700, 2.729000}, {120.055800, 2.986100},
        {120.108100, 2.986600}, {154.640700, 3.342900}, {154.693000, 3.343500}, {182.046900, 3.625700},
        {182.099200, 3.626300}, {207.330400, 3.886700}, {207.382700, 3.887200}, {228.132200, 4.101400},
        {228.184500, 4.102000}, {256.763800, 4.397000}, {256.816100, 4.397600}, {286.159500, 4.700600},
        {286.211800, 4.701100}, {310.537200, 4.952300}, {310.589500, 4.952900}, {334.112000, 5.195800},
        {334.164300, 5.196400}, {363.874200, 5.503300}, {363.926500, 5.503900}, {387.288800, 5.745200}
    }, false}, {{
        {-39.280950, -0.404950}, {-20.835150, -0.214750}, {-20.782850, -0.214250}, {-0.052321, -0.000550},
        {0.000000, 0.000000}, {21.365250, 0.220250}, {21.417600, 0.220850}, {26.726600, 0.275550},
        {26.853800, 0.276850}, {32.007300, 0.330050}, {32.244700, 0.332450}, {37.322250, 0.384850},
        {37.372450, 0.385350}, {42.899850, 0.442350}, {42.952200, 0.442850}, {71.880000, 0.741200},
        {71.932300, 0.741750}, {95.096350, 0.980680}, {95.148700, 0.981250}, {120.073800, 1.238370},
        {120.126100, 1.238890}, {154.658750, 1.595200}, {154.711050, 1.595770}, {182.064950, 1.878020},
        {182.117250, 1.878590}, {207.348450, 2.139010}, {207.400750, 2.139530}, {228.150250, 2.353730},
        {228.202550, 2.354300}, {256.781850, 2.649340}, {256.834150, 2.649910}, {286.177550, 2.952900},
        {286.229850, 2.953450}, {310.555250, 3.204650}, {310.607550, 3.205250}, {334.130050, 3.448150},
        {334.182350, 3.448750}, {363.892250, 3.755650}, {363.944550, 3.756250}, {387.280700, 3.997300}
    }, false}, {{
        {-39.289100, -2.153000}, {-20.817100, -1.962500}, {-20.764800, -1.962000}, {-0.034304, -1.748300},
        {0.018020, -1.747800}, {21.383300, -1.527500}, {21.435600, -1.526900}, {26.744600, -1.472200},
        {26.871800, -1.470900}, {32.025300, -1.417700}, {32.262700, -1.415300}, {37.340300, -1.362900},
        {37.390500, -1.362400}, {42.917900, -1.305400}, {42.970200, -1.304900}, {71.898000, -1.006500},
        {71.950300, -1.006000}, {95.114400, -0.767040}, {95.166700, -0.766500}, {120.091800, -0.509360},
        {120.144100, -0.508820}, {154.676800, -0.152500}, {154.729100, -0.151960}, {182.083000, 0.130340},
        {182.135300, 0.130880}, {207.366500, 0.391320}, {207.418800, 0.391860}, {228.168300, 0.606060},
        {228.220600, 0.606600}, {256.799900, 0.901680}, {256.852200, 0.902220}, {286.195600, 1.205200},
        {286.247900, 1.205800}, {310.573300, 1.457000}, {310.625600, 1.457600}, {334.148100, 1.700500},
        {334.200400, 1.701100}, {363.910300, 2.008000}, {363.962600, 2.008600}, {387.272600, 2.249400}
    }, false}, None, None, 30626, true, 30622, true, 426.584366},
{30626, {{
        {-39.493100, 4.874500}, {-21.021100, 5.064900}, {-20.837300, 5.066800}, {-0.238310, 5.279100},
        {-0.054446, 5.281000}, {21.179300, 5.499900}, {21.363100, 5.501800}, {26.485800, 5.554700},
        {26.799400, 5.557900}, {31.828500, 5.609700}, {32.190200, 5.613500}, {37.004400, 5.663100},
        {37.318000, 5.666300}, {42.713900, 5.722000}, {42.897700, 5.723900}, {71.694000, 6.020800},
        {71.877800, 6.022700}, {94.910400, 6.260300}, {95.094200, 6.262200}, {119.887800, 6.517900},
        {120.071600, 6.519800}, {154.472700, 6.874800}, {154.656600, 6.876700}, {181.878900, 7.157600},
        {182.062800, 7.159500}, {207.162400, 7.418500}, {207.346200, 7.420400}, {227.964200, 7.633200},
        {228.148100, 7.635100}, {256.595800, 7.928800}, {256.779700, 7.930700}, {285.991500, 8.232300},
        {286.175300, 8.234200}, {310.369100, 8.484100}, {310.553000, 8.486000}, {333.944000, 8.727600},
        {334.127800, 8.729500}, {363.706100, 9.035000}, {363.890000, 9.036900}, {387.068500, 9.276400}
    }, false}, {{
        {-39.382950, 3.108800}, {-21.002900, 3.298250}, {-20.819100, 3.300150}, {-0.220100, 3.512500},
        {-0.036233, 3.514400}, {21.197500, 3.733300}, {21.381350, 3.735200}, {26.504000, 3.788050},
        {26.817600, 3.791250}, {31.846750, 3.843100}, {32.208450, 3.846850}, {37.022650, 3.896450},
        {37.336200, 3.899700}, {42.732100, 3.955350}, {42.915950, 3.957250}, {71.712200, 4.254200},
        {71.896050, 4.256100}, {94.928600, 4.493700}, {95.112450, 4.495600}, {119.906000, 4.751300},
        {120.089850, 4.753200}, {154.490950, 5.108200}, {154.674800, 5.110100}, {181.897150, 5.391000},
        {182.081000, 5.392900}, {207.180650, 5.651900}, {207.364450, 5.653800}, {227.982450, 5.866650},
        {228.166300, 5.868550}, {256.614050, 6.162250}, {256.797900, 6.164150}, {286.009750, 6.465750},
        {286.193550, 6.467650}, {310.387350, 6.717550}, {310.571250, 6.719450}, {333.962250, 6.961050},
        {334.146050, 6.962950}, {363.724350, 7.268500}, {363.908250, 7.270400}, {387.178650, 7.510800}
    }, false}, {{
        {-39.272800, 1.343100}, {-20.984700, 1.531600}, {-20.800900, 1.533500}, {-0.201890, 1.745900},
        {-0.018020, 1.747800}, {21.215700, 1.966700}, {21.399600, 1.968600}, {26.522200, 2.021400},
        {26.835800, 2.024600}, {31.865000, 2.076500}, {32.226700, 2.080200}, {37.040900, 2.129800},
        {37.354400, 2.133100}, {42.750300, 2.188700}, {42.934200, 2.190600}, {71.730400, 2.487600},
        {71.914300, 2.489500}, {94.946800, 2.727100}, {95.130700, 2.729000}, {119.924200, 2.984700},
        {120.108100, 2.986600}, {154.509200, 3.341600}, {154.693000, 3.343500}, {181.915400, 3.624400},
        {182.099200, 3.626300}, {207.198900, 3.885300}, {207.382700, 3.887200}, {228.000700, 4.100100},
        {228.184500, 4.102000}, {256.632300, 4.395700}, {256.816100, 4.397600}, {286.028000, 4.699200},
        {286.211800, 4.701100}, {310.405600, 4.951000}, {310.589500, 4.952900}, {333.980500, 5.194500},
        {334.164300, 5.196400}, {363.742600, 5.502000}, {363.926500, 5.503900}, {387.288800, 5.745200}
    }, false}, None, None, None, false, 30624, true, 426.584313}
};
/**capture lanelet end */

double get_distance(ST_DPOINT p1, ST_DPOINT p2) {
    double dx = p2.x - p1.x;
    double dy = p2.y - p1.y;
    return sqrt(dx * dx + dy * dy);
}

/**
 * @brief Initializes the positions of the test and ego vehicles.
 * 
 * This function searches through the lane network to find the lanes
 * with IDs matching INIT_LANE_TEST and INIT_LANE_EGO. For each, it computes
 * the midpoint between the first left and right boundary points and stores
 * the result in the provided pointers.
 * 
 * @param tpx Pointer to store the x-coordinate of the test vehicle's initial position
 * @param tpy Pointer to store the y-coordinate of the test vehicle's initial position
 * @param epx Pointer to store the x-coordinate of the ego vehicle's initial position
 * @param epy Pointer to store the y-coordinate of the ego vehicle's initial position
 */
void initialize(double *tpx, double *tpy, double *epx, double *epy){
    int i = 0;
    ST_DPOINT right, left;

    for(i = 0; i < MAXL; i++){  // Loop through all lanes in the lane network
        if(laneNet[i].ID == INIT_LANE_TEST){
            (*tpx) = laneNet[i].center.points[0].x;
            (*tpy) = laneNet[i].center.points[0].y;
        }
        if(laneNet[i].ID == INIT_LANE_EGO){
            (*epx) = laneNet[i].center.points[0].x;
            (*epy) = laneNet[i].center.points[0].y;
        }
    }
}

int find_lane_index_by_id(id_t lane_id){
    for (int i = 0; i < MAXL; i++) {
        if(laneNet[i].ID == lane_id){
            return i;
        }
    }
    return -1;
}

void update_target(id_t lane_id, ST_DPOINT current, double speed, double period, ST_DPOINT *target, int *waypoint){
    int i = 0, lane_index = find_lane_index_by_id(INIT_LANE_TEST);
    double distance = 0;

    if((*waypoint) < MAXP){
        *target = laneNet[lane_index].center.points[*waypoint];
        if(target->x != None && target->y != None){
            distance = get_distance(current, *target);
            while(distance <= speed * period && (*waypoint) < MAXP){
                (*waypoint) = (*waypoint) + 1;            
                if((*waypoint) < MAXP){
                    *target = laneNet[lane_index].center.points[*waypoint];
                }else{
                    *target = laneNet[lane_index].center.points[MAXP - 1];
                }
                distance = get_distance(current, *target);
            }
        }else{
            // "None" needs to be dealt with
        }
    }else{
        *target = laneNet[lane_index].center.points[MAXP - 1];
    }
    distance = get_distance(current, *target);

    //printf("target %d: %f, %f. distance: %f\n", *waypoint, target->x, target->y, distance);
    //printf("current: %f, %f, %f, %f\n", tpx, tpy, tvx, tvy);
}

/**
 * @brief Update the testing vehicle's acceleration on x and y.
 *
 * This function calculates the testing vehicle's x and y accelerations such that 
 * the vehicle moves along the center line of the lane in the next P time units.
 * The resulting accelerations are scaled to stay within the given AMIN and AMAX bounds.
 *
 * @param tpx Current x position of the testing vehicle
 * @param tpy Current y position of the testing vehicle
 * @param tvx Current x velocity of the testing vehicle
 * @param tvy Current y velocity of the testing vehicle
 * @param tax Pointer to x acceleration of the testing vehicle (to be updated)
 * @param tay Pointer to y acceleration of the testing vehicle (to be updated)
 * @param epx Current x position of the ego vehicle
 * @param epy Current y position of the ego vehicle
 * @param evx Current x velocity of the ego vehicle
 * @param evy Current y velocity of the ego vehicle
 * @param eax Current x acceleration of the ego vehicle
 * @param eay Current y acceleration of the ego vehicle
 * @param P Time horizon for planning (in seconds)
 * @param AMIN Minimum allowed acceleration per axis [X, Y]
 * @param AMAX Maximum allowed acceleration per axis [X, Y]
 * @return true if a valid target point was found and acceleration was computed
 */
void get_action(double tpx, double tpy, double tvx, double tvy, double *tax, double *tay,
                double epx, double epy, double evx, double evy, double eax, double eay,
                double P, double AMINX, double AMINY, double AMAXX, double AMAXY, 
                double VMINX, double VMINY, double VMAXX, double VMAXY, int* waypoint) {
    int i = 0, lane_index = find_lane_index_by_id(INIT_LANE_TEST), minIndex = 0;
    ST_DPOINT start, end, current, target;
    double distance, minDis = DBL_MAX;
    double ax, ay, vx = tvx, vy = tvy;
    double scaleX = 1.0, scaleY = 1.0, scale = 0;
    
    current.x = tpx;
    current.y = tpy;
    update_target(INIT_LANE_TEST, current, sqrt(tvx*tvx+tvy*tvy), P, &target, waypoint);

    // Compute required acceleration using kinematic equation
    ax = 2.0 * (target.x - tpx - tvx * P) / (P * P);
    ay = 2.0 * (target.y - tpy - tvy * P) / (P * P);

    // Compute per-axis scaling factors
    if (ax > AMAXX) scaleX = AMAXX / ax;
    else if (ax < AMINX && ax != 0.0) scaleX = AMINX / ax;

    if (ay > AMAXY) scaleY = AMAXY / ay;
    else if (ay < AMINY && ay != 0.0) scaleY = AMINY / ay;

    // Use the smaller scaling factor to preserve direction
    scale = (fabs(scaleX) < fabs(scaleY)) ? scaleX : scaleY;

    // Apply scaling
    *tax = ax * scale;
    *tay = ay * scale;

    // Compute the future velocity on X and Y and regulate accelerations accordingly
    vx += *tax * P;
    vy += *tay * P;
    if(vx >= VMAXX || vx <= VMINX){
        *tax = 0;
    }
    if(vy >= VMAXY || vy <= VMINY)
    {
        *tay = 0;
    }
}

bool is_action_ok(double tpx, double tpy, double tvx, double tvy, double tax, double tay,
                double epx, double epy, double evx, double evy, double eax, double eay){
    /* test code */
    if(tpx == 0.0 && tpx == 0.0 && tvx == 0.0 && tvx == 0.0){
        if(tax == 1.0 && tay == -0.5){
            return true;
        }
        else{
            return false;
        }
    }

    return false;
}

int main()
{
    int waypoint = 0;
    double tpx, tpy, tvx = 0.1, tvy = 0, tax, tay;
    double epx, epy, evx = 0.1, evy = 0, eax = 0, eay = 0;
    const double P = 0.1;
    const double AMINX = -1, AMINY = -1, AMAXX = 1, AMAXY = 1;
    const double VMINX = -5, VMINY = -5, VMAXX = 8, VMAXY = 8;

    initialize(&tpx, &tpy, &epx, &epy);

    FILE *fp = fopen("/home/rong/Github/AutoScene/sampling.log", "w");
    if (fp == NULL) {
        printf("Error opening file for writing.\n");
        return 1;
    }

    //printf("start!\n");

    for (int i = 0; i < 500; i++) {
        get_action(tpx, tpy, tvx, tvy, &tax, &tay,epx, epy, evx, evy, eax, eay, P, 
            AMINX, AMINY, AMAXX, AMAXY, VMINX, VMINY, VMAXX, VMAXY, &waypoint);
        // Euler integration to update target's velocity and position
        tvx += tax * 0.1;
        tvy += tay * 0.1;
        tpx += tvx * 0.1;
        tpy += tvy * 0.1;

        // Write to file every 10 iterations
        if (i % 10 == 0) {
            fprintf(fp, "%d %f %f %f %f %f %f\n", i / 10, tpx, tpy, tvx, tvy, tax, tay);
        }
    }

    fclose(fp);
    return 0;
}