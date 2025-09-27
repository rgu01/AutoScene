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
            // Get the first point from left and right boundaries of the test lane
            right = laneNet[i].right.points[0];
            left = laneNet[i].left.points[0];

            // Compute the midpoint and store in test vehicle position
            (*tpx) = (right.x + left.x) / 2.0;
            (*tpy) = (right.y + left.y) / 2.0;
        }
        if(laneNet[i].ID == INIT_LANE_EGO){
            // Get the first point from left and right boundaries of the ego lane
            right = laneNet[i].right.points[0];
            left = laneNet[i].left.points[0];

            // Compute the midpoint and store in ego vehicle position
            (*epx) = (right.x + left.x) / 2.0;
            (*epy) = (right.y + left.y) / 2.0;
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

/**
 * @brief Returns the next ahead points on the left and right boundaries of the current lane
 * 
 * The function finds the nearest point on each boundary that lies ahead of the current
 * vehicle position, based on the direction of the velocity vector.
 * 
 * @param lane_id ID of the current traveling lane
 * @param px X-coordinate of the test vehicle's current position
 * @param py Y-coordinate of the test vehicle's current position
 * @param vx Velocity component along X
 * @param vy Velocity component along Y
 * @param left Pointer to store the next point on the left boundary
 * @param right Pointer to store the next point on the right boundary
 * @return true if ahead points were found, false otherwise
 */
bool get_ahead_lane_boundaries_ahead(id_t lane_id, double px, double py, double vx, double vy, ST_DPOINT *left, ST_DPOINT *right) {
    // Find the index of the lane in laneNet array
    int lane_index = find_lane_index_by_id(lane_id);
    if (lane_index == -1) return false;  // Lane not found

    ST_LANE *lane = &laneNet[lane_index];

    // Initialize indices and minimum projection distances
    int next_left_idx = -1;
    int next_right_idx = -1;
    double min_proj_left = DBL_MAX;
    double min_proj_right = DBL_MAX;

    // Compute normalized velocity vector for projection along travel direction
    double speed_sq = vx * vx + vy * vy;
    if (speed_sq < 1e-6) return false;  // Velocity too small to determine direction
    double inv_speed = 1.0 / sqrt(speed_sq);
    double dir_x = vx * inv_speed;
    double dir_y = vy * inv_speed;

    // Loop through left boundary points to find nearest point ahead
    for (int i = 0; i < MAXP; i++) {
        ST_DPOINT pt = lane->left.points[i];
        if (pt.x == 0 && pt.y == 0) break; // Assuming unused points are {0,0}

        double dx = pt.x - px;
        double dy = pt.y - py;
        double proj = dx * dir_x + dy * dir_y;  // Project vector onto velocity direction

        // Consider only points ahead and track the closest one
        if (proj > 0 && proj < min_proj_left) {
            min_proj_left = proj;
            next_left_idx = i;
        }
    }

    // Loop through right boundary points to find nearest point ahead
    for (int i = 0; i < MAXP; i++) {
        ST_DPOINT pt = lane->right.points[i];
        if (pt.x == 0 && pt.y == 0) break;

        double dx = pt.x - px;
        double dy = pt.y - py;
        double proj = dx * dir_x + dy * dir_y;

        if (proj > 0 && proj < min_proj_right) {
            min_proj_right = proj;
            next_right_idx = i;
        }
    }

    // Check if valid ahead points were found
    if (next_left_idx == -1 || next_right_idx == -1) return false;

    // Store the nearest ahead points in the provided pointers
    *left = lane->left.points[next_left_idx];
    *right = lane->right.points[next_right_idx];

    return true;
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
bool get_action(double tpx, double tpy, double tvx, double tvy, double *tax, double *tay,
                double epx, double epy, double evx, double evy, double eax, double eay,
                double P, double AMINX, double AMINY, double AMAXX, double AMAXY) {
    ST_DPOINT l, r;
    bool result = false;
    double cx, cy;
    double ax, ay;
    double scaleX = 1.0, scaleY = 1.0, scale;

    // Find the closest lane boundary points ahead of the testing vehicle
    result = get_ahead_lane_boundaries_ahead(INIT_LANE_TEST, tpx, tpy, tvx, tvy, &l, &r);

    //printf("(%f,%f,%f,%f)\n",l.x,l.y,r.x,r.y);

    if (result) {
        // Compute center line point
        cx = (l.x + r.x) / 2.0;
        cy = (l.y + r.y) / 2.0;

        // Compute required acceleration using kinematic equation
        ax = 2.0 * (cx - tpx - tvx * P) / (P * P);
        ay = 2.0 * (cy - tpy - tvy * P) / (P * P);

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
    } else {
        // If no valid point found, default to zero acceleration
        *tax = 0.0;
        *tay = 0.0;
    }

    return result;
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
    double tpx, tpy, tvx = 0.1, tvy = 0, tax, tay;
    double epx, epy, evx = 0.1, evy = 0, eax = 0, eay = 0;

    initialize(&tpx, &tpy, &epx, &epy);

    FILE *fp = fopen("/home/rong/Github/AutoScene/sampling.log", "w");
    if (fp == NULL) {
        printf("Error opening file for writing.\n");
        return 1;
    }

    for (int i = 0; i < 500; i++) {
        if(get_action(tpx, tpy, tvx, tvy, &tax, &tay,epx, epy, evx, evy, eax, eay, 0.1, -1, -1, 1, 1)){
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
    }

    fclose(fp);
    return 0;
}